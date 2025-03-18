from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from tqdm import tqdm  # Import tqdm for progress tracking

load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "database", "faiss_index")

def precompute_vectors():
    print("🔄 Initializing Embeddings Model...")
    embeddings = OllamaEmbeddings(model="all-minilm")

    # Load PDF files
    print("📂 Loading PDF documents...")
    pdf_path = os.path.join(BASE_DIR, "data", "knowledge_base")
    loader = PyPDFDirectoryLoader(pdf_path)
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents.")

    # Splitting documents into chunks with progress tracking
    print("✂️ Splitting documents into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = list(tqdm(text_splitter.split_documents(documents), desc="Splitting Progress", unit="chunk"))

    print(f"✅ Split into {len(final_documents)} chunks.")

    # Creating vector embeddings with progress tracking
    print("🔢 Creating vector embeddings...")
    vectors = FAISS.from_documents(tqdm(final_documents, desc="Embedding Progress", unit="chunk"), embeddings)

    # Save FAISS index
    print("💾 Saving FAISS index...")
    vectors.save_local(VECTOR_DB_PATH)
    print("✅ Vector DB Precomputed and Saved Successfully!")

if __name__ == "__main__":
    precompute_vectors()
