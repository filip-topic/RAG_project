import asyncio

from data_handling.document_loader import load_markdown
from data_handling.document_splitter import split_markdown
from data_handling.chunk_processor import get_title_and_summary, process_chunk

async def test_get_title_and_summary():
    print("\n------------------ BEGIN TESTING get_title_and_summary() ------------------\n")
    document = load_markdown()
    chunk = split_markdown(document[1].page_content)[0]
    print(get_title_and_summary(chunk, "example_url"))
    print("\n------------------ END TESTING get_title_and_summary() ------------------\n")


async def test_process_chunk():
    print("\n------------------ BEGIN TESTING process_chunk() ------------------\n")
    document = load_markdown()
    chunk = split_markdown(document[1].page_content)[0]
    processed_chunk = await process_chunk(chunk, 999, "example_url")
    print(processed_chunk.url)
    print(processed_chunk.title)
    print(processed_chunk.summary)
    print(processed_chunk.content)
    print(processed_chunk.metadata)
    print(processed_chunk.embedding)
    print("\n------------------ END TESTING process_chunk() ------------------\n")





#test_get_title_and_summary()
asyncio.run(test_process_chunk())   #WORKS