import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from helpers.prompts import CHUNK_SUMMARY_AGENT_PROMPT
from models.openai import get_one_shot_llm_response
from embeddings.embeddings_getter import get_embeddings
from config.config import CONFIG

@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: dict[str, any]
    embedding: list[float]

async def get_title_and_summary(chunk: str, url: str):

    try:
        response = await get_one_shot_llm_response(user_prompt=chunk, system_prompt=CHUNK_SUMMARY_AGENT_PROMPT)
        return response
    
    except Exception as e:
        print(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}
    
async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    
    extracted = await get_title_and_summary(chunk, url)

    embedding = await get_embeddings(chunk)

    metadata = {
        "source": CONFIG["data_source"]["website"],
        "chunk_size": len(chunk),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": urlparse(url).path
    }

    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted['title'],
        summary=extracted['summary'],
        content=chunk,  
        metadata=metadata,
        embedding=embedding
    )
    



