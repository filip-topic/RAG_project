from langchain.vectorstores.chroma import Chroma
from src.embeddings.embeddings_getter import get_embedding_function

CHROMA_PATH ="./chroma"

def retrieve_top_k_relevant_chunks(query_text: str, k=5):
    #prepare the database
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )

    # get 5 most relevant chunks
    results = db.similarity_search_with_score(query_text, k=k)

    return results

def test_ir():
    results = retrieve_top_k_relevant_chunks("What was the revenue in 2023?")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    print("\n------------------ BEGIN TESTING info_retreival() ------------------\n")
    print(context_text)
    print("\n------------------ END TESTING info_retreival() ------------------\n")

