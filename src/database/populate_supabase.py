import asyncio

from config import CONFIG
from data_handling.document_splitter import split_markdown
from data_handling.chunk_processor import process_chunk
from database.supabase_inserter import insert_chunk

async def process_store_and_populate_supabase(url: str = CONFIG["data_source"]["website"], markdown: str = None):
    #split doc into chunks
    chunks = split_markdown(markdown)

    #paralles process chunks
    tasks = [
        process_chunk(chunk, i, url)
        for i, chunk in enumerate(chunks)
    ]
    processed_chunks = await asyncio.gather(*tasks)

    # parallel store chunks
    insert_tasks = [
        insert_chunk(chunk)
        for chunk in processed_chunks
    ]
    await asyncio.gather(*insert_tasks)