from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, ModelRetry, RunContext
from typing import Optional, List
from pydantic import BaseModel
import logfire
from dataclasses import dataclass
from openai import AsyncOpenAI
from supabase import Client
import os
from dotenv import load_dotenv
import asyncio
from functools import partial
from typing import Any

from config import CONFIG
from generic_agent import PydanticAIDeps
from helpers.prompts import DATA_WARDEN_URL_SYSTEM_PROMPT, DATA_WARDEN_TITLE_SYSTEM_PROMPT, DATA_WARDEN_SUMMARY_SYSTEM_PROMPT, DATA_WARDEN_CHIEF_SYSTEM_PROMPT

class dataAgentDeps(BaseModel):
    dep1: str

# database
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase_client = Client(supabase_url, supabase_key)

# agent LLM
model = OpenAIModel(model_name = CONFIG["model"]["llm"], api_key = os.getenv("OPENAI_API"))
logfire.configure(send_to_logfire="if-token-present")

#print(supabase_client.table("site_pages").select("id" + ", " + "url").execute().data)

data_url_agent = Agent(
    model,
    system_prompt = DATA_WARDEN_URL_SYSTEM_PROMPT,
    deps_type = dataAgentDeps,
    retries = 2
)

data_title_agent = Agent(
    model,
    system_prompt = DATA_WARDEN_TITLE_SYSTEM_PROMPT,
    deps_type = dataAgentDeps,
    retries = 2
)

data_summary_agent = Agent(
    model,
    system_prompt = DATA_WARDEN_SUMMARY_SYSTEM_PROMPT,
    deps_type = dataAgentDeps,
    retries = 2
)

data_chief_agent = Agent(
    model,
    system_prompt = DATA_WARDEN_CHIEF_SYSTEM_PROMPT,
    deps_type = dataAgentDeps,
    retries = 2
)

# agent tool for fetching data from supabase
@data_url_agent.tool
async def get_url(ctx: RunContext[dataAgentDeps]):

    """
    Retrieve the column 'column' and id from the database.

    Args:
        ctx: Ignore this argument.

    Returns: 
        a list of URLs of all chunks in the database along with corresponding IDs 
    """

    try:
        response = supabase_client.table("site_pages").select("id, url").execute()
        if response:
            return response.data
        else:
            print ("The response is empty")
    except Exception as e:
        print(f"There was an error: {e}")



@data_title_agent.tool
async def get_title(ctx: RunContext[dataAgentDeps]):

    """
    Retrieve the column 'column' and id from the database.

    Args:
        ctx: Ignore this argument.

    Returns: 
        a list of titles of all chunks in the database along with corresponding IDs 
    """

    try:
        response = supabase_client.table("site_pages").select("id, title").execute()
        if response:
            return response.data
        else:
            print ("The response is empty")
    except Exception as e:
        print(f"There was an error: {e}")



@data_summary_agent.tool
async def get_summary(ctx: RunContext[dataAgentDeps]):

    """
    Retrieve the column 'column' and id from the database.

    Args:
        ctx: Ignore this argument.

    Returns: 
        a list of summaries of all chunks in the database along with corresponding IDs 
    """

    try:
        response = supabase_client.table("site_pages").select("id, summary").execute()
        if response:
            return response.data
        else:
            print ("The response is empty")
    except Exception as e:
        print(f"There was an error: {e}")



async def test_url_agent():
    deps = dataAgentDeps(
        dep1 = "bla"
    )

    result = await data_url_agent.run(
        "Show me the example of the weather agent.", 
        deps = deps
    )
    print('Response:', result.data)

if __name__ == "__main__":
    asyncio.run(test_url_agent())