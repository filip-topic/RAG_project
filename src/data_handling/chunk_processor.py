from helpers.prompts import CHUNK_SUMMARY_AGENT_PROMPT
from models.openai import get_one_shot_llm_response

def get_title_and_summary(chunk: str):

    try:
        response = get_one_shot_llm_response(user_prompt=chunk, system_prompt=CHUNK_SUMMARY_AGENT_PROMPT)
        return response
    
    except Exception as e:
        print(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}
    



