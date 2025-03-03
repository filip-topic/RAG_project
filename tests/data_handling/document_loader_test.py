from data_handling.document_loader import load_pdf, load_markdown

def test_load_pdf():
    documents = load_pdf()
    print("\n------------------ BEGIN TESTING load_pdf() ------------------\n")
    print(documents[1])
    print("\n------------------ END TESTING load_pdf() ------------------\n")

def test_load_markdown():
    documents = load_markdown()
    print("\n------------------ BEGIN TESTING load_markdown() ------------------\n")
    print(documents[1])
    print("\n------------------ END TESTING load_markdown() ------------------\n")



test_load_pdf()   
test_load_markdown()    