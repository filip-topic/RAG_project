from pydatic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, ModelRetry, RunContext
import logfire
from dataclasses import dataclass
from openai import AsyncOpenAI
from supabase import Client
import asyncio

from config.config import CONFIG
from helpers.prompts import RAG_AGENT_SYSTEM_PROMPT
from embeddings.embeddings_getter import get_embeddings

model = OpenAIModel(CONFIG["model"]["llm"])
logfire.configure(send_to_logfire="if-token-present")

# step n1 in creating agent: agent dependancies
@dataclass
class PydanticAIDeps:
    supabase: Client
    openai_client: AsyncOpenAI

simple_agent = Agent(
    model,
    system_prompt = RAG_AGENT_SYSTEM_PROMPT,
    deps_type = PydanticAIDeps,
    retries = 2
)

@simple_agent.tool
async def retrieve_relevant_chunks(ctx: RunContext[PydanticAIDeps], user_query: str) -> str:
    """
    Retrieve relevant documentation chunks based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top 5 most relevant documentation chunks
    """

    try:
        query_embedding = await get_embeddings(user_query)

        result = ctx.deps.supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {'source': 'pydantic_ai_docs'}
            }
        ).execute()

        if not result.data:
            return "No relevant documentation found."
    
        # Format the results
        formatted_chunks = []
        for doc in result.data:
            chunk_text = f"""
                # {doc['title']}

                {doc['content']}
                """
            formatted_chunks.append(chunk_text)
            
        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}"
