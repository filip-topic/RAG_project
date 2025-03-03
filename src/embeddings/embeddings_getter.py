from langchain.embeddings import HuggingFaceEmbeddings

from config.config import config

def get_embedding_function():
    embeddings = HuggingFaceEmbeddings(model_name=config["tokenizer"]["model"])
    return embeddings