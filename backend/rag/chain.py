"""
RAG chain component for conversational question answering.
LangChain >= 0.2.x compatible (LCEL-native, no legacy memory).
"""

from typing import List, Tuple
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
)
from backend.core.llm import get_llm
from backend.core.prompts import CONVERSATIONAL_PROMPT
from backend.rag.retriever import get_vectorstore


# ---------------------------------------------------------
# Basic Retrieval Chain
# ---------------------------------------------------------
def create_retrieval_chain(retriever: BaseRetriever | None = None):
    """
    Create a simple retrieval-based QA chain.
    """
    if retriever is None:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = get_llm()

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | CONVERSATIONAL_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain


# ---------------------------------------------------------
# RAG Chain (Non-conversational)
# ---------------------------------------------------------
def get_rag_chain(retriever: BaseRetriever | None = None):
    """
    Get a standard RAG QA chain.
    """
    if retriever is None:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = get_llm()

    chain = (
        RunnablePassthrough.assign(
            context=lambda x: retriever.invoke(x["question"])
        )
        | CONVERSATIONAL_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain


# ---------------------------------------------------------
# Conversational RAG Chain (LCEL-correct)
# ---------------------------------------------------------
def get_conversational_chain(retriever: BaseRetriever | None = None):
    """
    Get a conversational RAG chain.
    Chat history is passed explicitly (LangChain 0.2+ standard).
    """
    if retriever is None:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = get_llm()

    def normalize_question(inputs: dict) -> str:
        return inputs["question"]

    chain = (
        RunnablePassthrough.assign(
            question=RunnableLambda(normalize_question),
            context=lambda x: retriever.invoke(x["question"]),
        )
        | CONVERSATIONAL_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain


# ---------------------------------------------------------
# Public API Helpers
# ---------------------------------------------------------
def ask_question(
    question: str,
    chain=None
) -> Tuple[str, List[Document]]:
    """
    Ask a single question using RAG.
    """
    if chain is None:
        chain = get_rag_chain()
        vectorstore = get_vectorstore()
        sources = vectorstore.similarity_search(question, k=5)
    else:
        sources = []

    answer = chain.invoke({"question": question})

    return answer, sources


def conversational_chat(
    question: str,
    chat_history: List[Tuple[str, str]] | None = None,
    chain=None,
) -> str:
    """
    Conversational chat with explicit history handling.
    """
    if chain is None:
        chain = get_conversational_chain()

    if chat_history is None:
        chat_history = []

    formatted_history = "\n".join(
        f"Human: {q}\nAssistant: {a}"
        for q, a in chat_history
    )

    inputs = {
        "question": question,
        "chat_history": formatted_history,
    }

    answer = chain.invoke(inputs)

    return answer

