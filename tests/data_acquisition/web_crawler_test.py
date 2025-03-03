import asyncio

from data_acquisition.web_crawler import get_urls, scrape_entire_page

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

test_get_urls()

asyncio.run(test_scrape_entire_page())