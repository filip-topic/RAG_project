from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import argparse
import os


from src.information_retreival.information_retreiver import retrieve_top_k_relevant_chunks, test_ir
from src.models.openai import get_one_shot_llm_response
#from database import populate_chroma_database
from src.helpers.prompts import BASIC_RAG_PROMPT

CHROMA_PATH = "./chroma"
OPENAI_API = os.getenv("OPENAI_API")


def main():
    '''parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text'''
    query_text = "What was the revenue in 2023?"
    query_rag(query_text)


def query_rag(query_text: str):

    # get 5 most relevant chunks
    results = retrieve_top_k_relevant_chunks(query_text, 5)

    # engineer the prompt
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(BASIC_RAG_PROMPT)
    prompt = prompt_template.format(context=context_text, question=query_text)

    #feed the prompt into the LLM and get the response
    model_response = get_one_shot_llm_response(prompt)


    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {model_response}\nSources: {sources}"
    print(formatted_response)
    return model_response

#main()

if __name__ == "__main__":
    main()