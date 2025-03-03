from information_retreival.information_retreiver import retrieve_top_k_relevant_chunks

def test_ir():
    results = retrieve_top_k_relevant_chunks("What was the revenue in 2023?")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    print("\n------------------ BEGIN TESTING info_retreival() ------------------\n")
    print(context_text)
    print("\n------------------ END TESTING info_retreival() ------------------\n")

test_ir()