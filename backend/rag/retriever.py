"""
Retriever component for RAG pipeline using ChromaDB.
"""
import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from backend.core.config import settings


def get_embeddings():
    """
    Get the embeddings model based on configuration.
    
    Returns:
        An embeddings model instance.
    """
    return OpenAIEmbeddings(api_key=settings.openai_api_key)


def get_vectorstore(persist_directory: str = None) -> Chroma:
    """
    Get or create the ChromaDB vector store.
    
    Args:
        persist_directory: Directory to persist the vector store.
    
    Returns:
        A ChromaDB vector store instance.
    """
    persist_directory = persist_directory or settings.chroma_db_path
    
    # Ensure directory exists
    os.makedirs(persist_directory, exist_ok=True)
    
    embeddings = get_embeddings()
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=settings.chroma_collection_name
    )
    
    return vectorstore


def add_documents_to_vectorstore(documents: List[Document]) -> None:
    """
    Add documents to the vector store.
    
    Args:
        documents: List of documents to add.
    """
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    print(f"Added {len(documents)} documents to vector store")


def similarity_search(query: str, k: int = 5) -> List[Document]:
    """
    Search for similar documents.
    
    Args:
        query: The search query.
        k: Number of results to return.
    
    Returns:
        List of similar documents.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results


def similarity_search_with_score(query: str, k: int = 5) -> List[tuple]:
    """
    Search for similar documents with scores.
    
    Args:
        query: The search query.
        k: Number of results to return.
    
    Returns:
        List of tuples containing (document, score).
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results


def delete_collection() -> None:
    """
    Delete the current collection.
    """
    vectorstore = get_vectorstore()
    vectorstore.delete_collection()
    print("Collection deleted")


def get_collection_stats() -> dict:
    """
    Get statistics about the current collection.
    
    Returns:
        Dictionary containing collection stats.
    """
    vectorstore = get_vectorstore()
    count = vectorstore._collection.count()
    return {"document_count": count}

