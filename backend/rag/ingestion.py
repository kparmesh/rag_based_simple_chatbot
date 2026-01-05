"""
Document ingestion for RAG pipeline.
"""
import os
import json
from typing import List, Any
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

    supported_extensions = (".txt", ".pdf", ".docx", ".csv", ".json")

    for filename in os.listdir(documents_path):
        file_path = os.path.join(documents_path, filename)

        if not os.path.isfile(file_path):
            continue

        if not filename.lower().endswith(supported_extensions):
            continue

        try:
            # 🔹 JSON handling
            if filename.lower().endswith(".json"):
                json_docs = load_json_file(file_path)
                documents.extend(json_docs)
                print(f"Loaded JSON: {filename}")
                continue

            # 🔹 Existing loaders (PDF, TXT, etc.)
            loader = get_loader(file_path)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {filename}")

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    return documents


def load_json_file(file_path: str) -> List[Document]:
    """
    General-purpose JSON loader for vector DB ingestion.
    Works with ANY table dump or JSON structure.
    """
    documents: List[Document] = []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = os.path.basename(file_path)

    # Case 1: List of rows (most table dumps)
    if isinstance(data, list):
        for idx, row in enumerate(data):
            text = json_to_text(row)
            if not text.strip():
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "type": "json_table",
                        "row_index": idx
                    }
                )
            )

    # Case 2: Single object
    elif isinstance(data, dict):
        text = json_to_text(data)
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "type": "json_object"
                    }
                )
            )

    return documents


def json_to_text(obj: Any, parent_key: str = "") -> str:
    """
    Recursively convert ANY JSON object into clean, readable text.
    """
    lines = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, (dict, list)):
                nested_text = json_to_text(value, full_key)
                if nested_text:
                    lines.append(nested_text)
            else:
                lines.append(f"{full_key}: {value}")

    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            lines.append(json_to_text(item, f"{parent_key}[{idx}]"))

    return "\n".join(filter(None, lines))


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

