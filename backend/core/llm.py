from langchain_openai import ChatOpenAI
from backend.core.config import settings


def get_llm() -> any:
    """
    Get the LLM instance based on the configured provider.
    
    Returns:
        An LLM instance.
    """
    
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model_name=settings.model_name,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )
