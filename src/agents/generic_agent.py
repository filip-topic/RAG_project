'''import sys

# Print the list of paths Python checks for modules
for path in sys.path:
    print(path)'''

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic import BaseModel
import logfire
from dataclasses import dataclass
from openai import AsyncOpenAI
from supabase import Client
import os

from config import CONFIG
from helpers.prompts import MAIN_AGENT_SYSTEM_PROMPT
from embeddings.embeddings_getter import get_embeddings


model = OpenAIModel(model_name = CONFIG["model"]["llm"], api_key = os.getenv("OPENAI_API"))
logfire.configure(send_to_logfire="if-token-present")

# step n1 in creating agent: agent dependancies
@dataclass
class PydanticAIDeps(BaseModel):
    supabase: Client
    openai_client: AsyncOpenAI

    class Config:
         arbitrary_types_allowed = True

generic_agent = Agent(
    model,
    system_prompt = MAIN_AGENT_SYSTEM_PROMPT,
    deps_type = PydanticAIDeps,
    retries = 2
)

@generic_agent.tool
async def retrieve_relevant_chunks(ctx: RunContext[PydanticAIDeps], user_query: str) -> str:
    """
    Retrieve relevant chunks based on the query with RAG.
    
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
    
@generic_agent.tool
async def list_documentation_pages(ctx: RunContext[PydanticAIDeps]) -> list[str]:
    
    f"""
    Retrieve a list of all available web pages from {CONFIG["data_source"]["website"]}.
    
    Returns:
        List[str]: List of unique URLs for all web pages
    """

    try:
        # Query Supabase for unique URLs where source is pydantic_ai_docs
        result = ctx.deps.supabase.from_('site_pages') \
            .select('url') \
            .execute()
        
        if not result.data:
            return []
            
        # Extract unique URLs
        urls = sorted(set(doc['url'] for doc in result.data))
        return urls
        
    except Exception as e:
        print(f"Error retrieving documentation pages: {e}")
        return []
    
@generic_agent.tool
async def get_page_content(ctx: RunContext[PydanticAIDeps], url: str) -> str:
    """
    Retrieve the full content of a specific page by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        url: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = ctx.deps.supabase.from_('site_pages') \
            .select('title, content, chunk_number') \
            .eq('url', url) \
            .order('chunk_number') \
            .execute()
        
        if not result.data:
            return f"No content found for URL: {url}"
            
        # Format the page with its title and all chunks
        page_title = result.data[0]['title'].split(' - ')[0]  # Get the main title
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result.data:
            formatted_content.append(chunk['content'])
            
        # Join everything together
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"
    

