from data_handling.document_splitter import split_pdf_list, split_markdown
from data_handling.document_loader import load_pdf, load_markdown

def test_split_pdf():
    documents = load_pdf()
    chunks = split_pdf_list(documents)
    print("\n------------------ BEGIN TESTING split_documents() ------------------\n")
    print(chunks[54])
    print("\n------------------ END TESTING split_documents() ------------------\n")

def test_split_markdown():
    documents = load_markdown()
    chunks = split_markdown(documents[0].page_content)
    print("\n------------------ BEGIN TESTING split_documents() ------------------\n")
    print(chunks[0])
    print("\n------------------ END TESTING split_documents() ------------------\n")



test_split_pdf()
test_split_markdown()