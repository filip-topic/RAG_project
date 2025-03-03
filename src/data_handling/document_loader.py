from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader

PDF_DATA_PATH = "./data/pdf"
MARKDOWN_DATA_PATH = "./data/markdown"

def load_pdf():
    document_loader = PyPDFDirectoryLoader(PDF_DATA_PATH)
    return document_loader.load()

def load_markdown():
    markdown_loader = DirectoryLoader(MARKDOWN_DATA_PATH, glob="*.md", loader_cls=lambda file_path: TextLoader(file_path, encoding="utf-8"))
    return markdown_loader.load()
