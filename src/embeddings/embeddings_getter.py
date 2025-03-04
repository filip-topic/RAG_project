from langchain.embeddings import HuggingFaceEmbeddings
from openai import AsyncOpenAI
import os

from config import CONFIG

def get_embedding_function():
    embeddings = HuggingFaceEmbeddings(model_name=CONFIG["tokenizer"]["model"])
    return embeddings

async def get_embeddings(text: str) -> list[float]:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API"))
    
    try:
        response = await client.embeddings.create(
            input = text,
            model = CONFIG["model"]["embedding"]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536
        
