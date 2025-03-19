import os
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = Path(__file__).resolve().parent.parent.parent
VECTOR_DB_PATH = BASE_DIR / "data" / "database" / "faiss_index"

def load_vector_db():
    if os.path.exists(VECTOR_DB_PATH):
        return FAISS.load_local(VECTOR_DB_PATH, HuggingFaceEmbeddings(model="all-MiniLM-L6-v2"), allow_dangerous_deserialization=True)
    return None