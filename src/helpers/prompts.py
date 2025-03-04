from config.config import CONFIG

BASIC_RAG_PROMPT = """
    I will give you 5 chunks of text which may or may not have information relevant to the questionI want to ask.
    Chunks are separated by '---'. Answer the question based only on the following context:

    {context}

    CONTEXT OVER

    Answer the following question based only on the above context and say which chunk contains the most relevant information (if any): {question}
"""


CHUNK_SUMMARY_AGENT_PROMPT = """
    Your job is to extract a title and summary from chunks of text.
    I will give you the chunk of text and I want you to eturn a JSON object with keys 'title' and 'summary'. 
    If the chunk seems like the start of a document, extract the title of it, but if not, them come up with a brief description of what the chunk is about.
    For the summary: come up with a short summary of the main points in the chunk.
    Keep both the title and summary concise and informative.
"""

RAG_AGENT_SYSTEM_PROMPT = f"""
    You are an expert at the {CONFIG["data_source"]["website"]} website - a website that you have complete access to.

    Your only job is to assist with this and you don't answer other questions besides describing what you are able to do.

    Don't ask the user before taking an action, just do it. Always make sure you look at the provided data with the provided tools before answering the user's question unless you have already.

    When you first look at the provided data, always start with RAG.
    Then also always check the list of available documentation pages and retrieve the content of page(s) if it'll help.

    Always let the user know when you didn't find the answer in the data or the right URL - be honest.
"""