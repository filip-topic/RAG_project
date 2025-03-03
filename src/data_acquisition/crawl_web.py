import os
import asyncio
import re

from data_acquisition.web_crawler import scrape_entire_page
from config import CONFIG


data_path = "./data/markdown"
#data_path = os.getcwd() +"/data/markdown"
os.makedirs(data_path, exist_ok=True)

url = CONFIG["data_source"]["website"]

def sanitize_filename(url):
    return re.sub(r'[<>:"/\\|?*]', '_', url)

async def main():

    pages = await scrape_entire_page(url)

    # Loop through each page and save it as a markdown file
    for content in pages:
        file_name = sanitize_filename(content.url)+".md"  # Naming convention: page_1.md, page_2.md, etc.
        file_path = os.path.join(data_path, file_name)
        
        # Write to the markdown file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.markdown_v2.raw_markdown)

        print(f"Saved: {file_path}")

    print("All Markdown files have been saved.")

asyncio.run(main())