"""
Pydantic schemas for chat API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Chat schemas
class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[int] = Field(None, description="Conversation ID for continuity")
    use_history: bool = Field(True, description="Whether to use conversation history")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    answer: str = Field(..., description="Assistant's response")
    conversation_id: int = Field(..., description="Conversation ID")
    sources: Optional[List[dict]] = Field(None, description="Source documents used")


# Document schemas
class DocumentInfo(BaseModel):
    """Schema for document information."""
    id: int
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    chunk_count: int
    indexed_at: datetime
    status: str


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    filename: str
    status: str
    chunks_created: int


# Ingestion schemas
class IngestionStatus(BaseModel):
    """Schema for ingestion status."""
    status: str
    documents_loaded: int
    chunks_created: int
    vectorstore_count: int


# Conversation schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    conversations: List[ConversationResponse]
    total: int

