"""
Document ingestion for RAG pipeline.
"""
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.core.config import settings
from pathlib import Path

def get_loader(file_path: str):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return PyPDFLoader(file_path)   # ✅ no encoding

    if extension == ".txt":
        return TextLoader(file_path, encoding="utf-8")

    if extension == ".csv":
        return CSVLoader(file_path, encoding="utf-8")

    raise ValueError(f"Unsupported file type: {extension}")
    

def load_documents(documents_path: str | None = None) -> list[Document]:
    documents_path = documents_path or settings.documents_path

    if not os.path.exists(documents_path):
        os.makedirs(documents_path, exist_ok=True)
        return []

    documents: list[Document] = []

    # ✅ MUST be strings only
    supported_extensions = (".txt", ".pdf", ".docx", ".csv")

    for filename in os.listdir(documents_path):
        file_path = os.path.join(documents_path, filename)

        if not os.path.isfile(file_path):
            continue

        if not filename.lower().endswith(supported_extensions):
            continue

        try:
            loader = get_loader(file_path)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {filename}")

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    return documents


def split_documents(documents: List[Document] = None) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        documents: List of documents to split.
    
    Returns:
        List of document chunks.
    """
    if documents is None:
        documents = load_documents()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata about source
    for chunk in chunks:
        if "source" not in chunk.metadata:
            chunk.metadata["source"] = chunk.metadata.get("source", "unknown")
    
    return chunks


def ingest_documents() -> int:
    """
    Main function to ingest all documents.
    
    Returns:
        Number of chunks created.
    """
    documents = load_documents()
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return len(chunks)

