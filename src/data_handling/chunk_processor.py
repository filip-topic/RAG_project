from dataclasses import dataclass
import asyncio

from src.helpers.prompts import CHUNK_SUMMARY_AGENT_PROMPT
from src.models.openai import get_one_shot_llm_response
from src.data_handling.document_loader import load_markdown
from src.data_handling.document_splitter import split_markdown

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
    
def test_get_title_and_summary():
    print("\n------------------ BEGIN TESTING get_title_and_summary() ------------------\n")
    document = load_markdown()
    chunk = split_markdown(document[1].page_content)[0]
    print(get_title_and_summary(chunk))
    print("\n------------------ END TESTING get_title_and_summary() ------------------\n")
    
#test_get_title_and_summary()   #WORKS

