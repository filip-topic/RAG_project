from supabase import create_client, Client
import os
from dotenv import load_dotenv
import asyncio

from data_handling.chunk_processor import ProcessedChunk
from config import CONFIG
from data_handling.document_splitter import split_markdown
from data_handling.chunk_processor import process_chunk

load_dotenv()

"""print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY')}")"""

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def insert_chunk(chunk: ProcessedChunk):
    try:
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding
        }

        result = supabase.table("site_pages").insert(data).execute()
        print(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
        return result
    except Exception as e:
        print (f"Error inserting chunk {e}")
        return None
    
    
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

        