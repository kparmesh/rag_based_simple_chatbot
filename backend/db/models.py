from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.db.session import Base


class User(Base):
    """Model for storing users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationship to submissions
    submissions = relationship("Submission", back_populates="user", cascade="all, delete")


class Conversation(Base):
    """Model for storing conversations."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete")


class Message(Base):
    """Model for storing chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50))  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    """Model for tracking indexed documents."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    indexed_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String(50), default="pending")  # 'pending', 'indexed', 'error'


class Submission(Base):
    """Model for storing questionnaire submissions."""
    
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    questionnaire_title = Column(String(255), nullable=False)
    step = Column(Integer, default=1)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationship to user
    user = relationship("User", back_populates="submissions")

