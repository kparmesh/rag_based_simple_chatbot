import uuid
from sqlalchemy import Column, Integer, String, DateTime, Boolean, event, ForeignKey, Text, Enum
from datetime import datetime, timezone
from backend.db.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    username = Column(String(150), unique=True, index=True, nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    full_name = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    submissions = relationship(
        "Submission",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# 🔹 Auto-fill full_name
@event.listens_for(User, "before_insert")
@event.listens_for(User, "before_update")
def set_full_name(mapper, connection, target):
    if target.first_name or target.last_name:
        target.full_name = " ".join(
            filter(None, [target.first_name, target.last_name])
        )
    else:
        target.full_name = None


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    questionnaire_title = Column(String(255), nullable=False)
    step = Column(Integer, default=1)
    is_complete = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="submissions")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(255), default="New Conversation")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(
        Enum(
            "user",
            "assistant",
            name="message_role_enum",
            native_enum=True,
        ),
        nullable=False
    )

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

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

