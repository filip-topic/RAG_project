from data_handling.document_loader import load_markdown
from data_handling.document_splitter import split_markdown

from data_handling.chunk_processor import get_title_and_summary

def test_get_title_and_summary():
    print("\n------------------ BEGIN TESTING get_title_and_summary() ------------------\n")
    document = load_markdown()
    chunk = split_markdown(document[1].page_content)[0]
    print(get_title_and_summary(chunk))
    print("\n------------------ END TESTING get_title_and_summary() ------------------\n")






test_get_title_and_summary()