from openai import AsyncOpenAI
import os
import json

from config import CONFIG

async def get_one_shot_llm_response(user_prompt: str, system_prompt: str = None):

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API"))

    if system_prompt:
        response = await client.chat.completions.create(
            model=CONFIG["model"]["llm"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format = {"type": "json_object"}
        )

    else:
        response = await client.chat.completions.create(
        model=CONFIG["model"]["llm"],
        messages=[{"role": "user", "content": user_prompt}]
        )
        
    response_content = response.choices[0].message.content
    if system_prompt:
        response_content = json.loads(response_content)
    return response_content

