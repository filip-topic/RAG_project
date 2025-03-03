from dataclasses import dataclass
import asyncio

from helpers.prompts import CHUNK_SUMMARY_AGENT_PROMPT
from models.openai import get_one_shot_llm_response
from data_handling.document_loader import load_markdown
from data_handling.document_splitter import split_markdown

@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: dict[str, any]
    embedding: list[float]

def get_title_and_summary(chunk: str):

    try:
        response = get_one_shot_llm_response(user_prompt=chunk, system_prompt=CHUNK_SUMMARY_AGENT_PROMPT)
        return response
    
    except Exception as e:
        print(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}
    



