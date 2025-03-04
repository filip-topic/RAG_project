import asyncio
from crawl4ai import *
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
import requests
from xml.etree import ElementTree
from crawl4ai import RateLimiter

from config import CONFIG
from database.supabase_inserter import process_store_and_populate_supabase



async def scrape_single_page(url: str = "https://www.nbcnews.com/business"):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return result.markdown

def get_urls(url: str = CONFIG["data_source"]["website"]) -> list[str]:
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

# this is a sync function. It simply returns all pages
async def scrape_entire_page(url: str = CONFIG["data_source"]["website"]) -> list[str]:

    pages =[]

    urls = get_urls(url)

    browser_config = BrowserConfig(
        headless=True, 
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )

    crawler_config = CrawlerRunConfig(
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
            config=crawler_config,
            dispatcher=dispatcher
        )

        # Process all results after completion
        for result in results:
            if result.success:
                pages.append(result)
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")
    
    return pages





# Create a RateLimiter with custom settings
rate_limiter = RateLimiter(
    base_delay=(8, 15),  # Random delay between 2-4 seconds
    max_delay=20,         # Cap delay at 30 seconds
    max_retries=5,          # Retry up to 5 times on rate-limiting errors
    rate_limit_codes=[429, 503]  # Handle these HTTP status codes
)

# this is async crawler function
async def parallel_scrape(url: str = CONFIG["data_source"]["website"], max_concurrent: int = 1):

    urls = get_urls(url)

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create a RateLimiter with custom settings
    rate_limiter = RateLimiter(
        base_delay=(10, 20),  # Random delay between 2-4 seconds
        max_delay=30,         # Cap delay at 30 seconds
        max_retries=5,          # Retry up to 5 times on rate-limiting errors
        rate_limit_codes=[429, 503]  # Handle these HTTP status codes
    )


    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id="session1"
                )
                if result.success:
                    print(f"Successfully crawled: {url}")
                    await process_store_and_populate_supabase(url, result.markdown_v2.raw_markdown)
                else:
                    print(f"Failed: {url} - Error: {result.error_message}")
        
        # Process all URLs in parallel with limited concurrency
        await asyncio.gather(*[process_url(url) for url in urls])
    finally:
        await crawler.close()



    