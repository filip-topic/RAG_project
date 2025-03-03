from embeddings.embeddings_getter import get_embeddings

def test_get_embeddings():
    print("-------------- START TESTING get_embeddings() ---------------")
    embeddings = get_embeddings(text="Hello, how are you today?")
    print(embeddings)
    print("-------------- END TESTING get_embeddings() ---------------")

test_get_embeddings()