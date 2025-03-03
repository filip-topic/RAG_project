import asyncio
from crawl4ai import *
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
import requests
from xml.etree import ElementTree
from crawl4ai import RateLimiter



async def scrape_single_page(url: str = "https://www.nbcnews.com/business"):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        print(result.markdown)

def get_urls(url: str = "https://ai.pydantic.dev") -> list[str]:
    sitemap_url = url + "/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []
    
rate_limiter = RateLimiter(
    base_delay=(2.0, 4.0),  # Random delay between 2-4 seconds
    max_delay=30.0,         # Cap delay at 30 seconds
    max_retries=5,          # Retry up to 5 times on rate-limiting errors
    rate_limit_codes=[429, 503]  # Handle these HTTP status codes
)

async def scrape_entire_page(url: str = "https://ai.pydantic.dev") -> list[str]:

    pages =[]

    urls = get_urls(url)

    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False  # Default: get all results at once
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=90.0,
        check_interval=1.0,
        max_session_permit=10,
        monitor=CrawlerMonitor(
            max_visible_rows=10,
            display_mode=DisplayMode.DETAILED
        )
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Get all results at once
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )

        # Process all results after completion
        for result in results:
            if result.success:
                pages.append(result)
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")
    
    return pages
    
def test_get_urls():
    urls = get_urls()
    print("--------------- BEGIN get_urls() TESTING --------------------")
    for i, url in enumerate(urls):
        print(f"URL {i}: " + url)
        print("-----")
    print("--------------- END get_urls() TESTING --------------------")

async def test_scrape_entire_page():
    pages = await scrape_entire_page()
    print("--------------- BEGIN scrape_entire_page() TESTING --------------------")
    print(pages[0])
    print("--------------- END scrape_entire_page() TESTING --------------------")
    pass


if __name__ == "__main__":
    #asyncio.run(scrape_single_page())
    #test_get_urls()   #WORKS
    asyncio.run(test_scrape_entire_page())
    pass