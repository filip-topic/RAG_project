from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

from data_handling.document_loader import load_pdf, load_markdown
from config import CONFIG

def split_pdf_list(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CONFIG["chunks"]["chunk_size"]["pdf"],  
        chunk_overlap=500,  
        separators=["\n\n", "\n", ".", " "]  
    )
    return text_splitter.split_documents(documents)


# splits markdown into chunks, respecting code blocks, paragraphs and sentences
def split_markdown(text: str, chunk_size: int = CONFIG["chunks"]["chunk_size"]["markdown"]):

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        
        if end >= text_length:
            chunks.append(text[start:].strip())
            break
        
        #finds code blocks
        chunk = text[start:end]
        code_block = chunk.rfind("```")
        if code_block != -1 and code_block > chunk_size*0.3:
            end = start + code_block

        # tries to break at paragraphs
        elif "\n\n" in chunk:
            last_break = chunk.rfind("\n\n")
            if last_break > chunk_size * 0.3:
                end = start + last_break

        elif ". " in chunk:
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.3:
                end = start + last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start+1, end)

    return chunks    
    