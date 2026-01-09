from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    DocumentUploadResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
)
from backend.rag.chain import (
    get_conversational_chain,
    ask_question
)
from backend.rag.ingestion import load_documents, split_documents
from backend.rag.retriever import add_documents_to_vectorstore, get_collection_stats, get_vectorstore
from backend.rag.retriever import similarity_search
from backend.db.models import Conversation, Message, Document as DocumentModel
from datetime import datetime, timezone
import shutil
import os
from typing import List


router = APIRouter()


# In-memory storage for chains (in production, use Redis or similar)
conversation_chains = {}

async def safe_context(docs: list) -> str:
    if not docs:
        return "NO_RELEVANT_CONTEXT"
    return "\n\n".join(d.page_content for d in docs)

def generate_title_from_message(message: str) -> str:
    """Generate a title from a message by taking the first N words."""
    words = message.strip().split()
    title = " ".join(words[:8])
    return title + "..." if len(words) > 8 else title

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint for conversational question answering.
    """
    # Get or create conversation
    conversation_id = request.conversation_id
    if conversation_id is None:
        conversation = Conversation(title=generate_title_from_message(request.message))
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
    else:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get conversation history
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    chat_history = [(msg.role, msg.content) for msg in messages]
    
    # ---- retrieve documents FIRST ----
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(request.message, k=5)
    context = await safe_context(docs)

    # ---- block hallucinations early ----
    if context == "NO_RELEVANT_CONTEXT":
        answer = "I don’t have this information right now... maybe in future I can help you better."
    else:
        if request.use_history:
            if conversation_id not in conversation_chains:
                conversation_chains[conversation_id] = get_conversational_chain()

            chain = conversation_chains[conversation_id]
            answer = chain.invoke({
                "question": request.message,
                "context": context,
                "chat_history": "\n".join(
                    f"Human: {q}\nAssistant: {a}"
                    for q, a in chat_history
                )
            })
        else:
            answer, _ = ask_question(request.message)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )
    db.add(assistant_message)
    
    # Update conversation
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return ChatResponse(
        answer=answer,
        conversation_id=conversation_id,
    )


@router.get("/chat/{conversation_id}/messages", response_model=List[ChatMessage])
async def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all messages in a conversation.
    """
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return [ChatMessage(role=msg.role, content=msg.content) for msg in messages]


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for indexing.
    """
    documents_path = "./data/documents"
    os.makedirs(documents_path, exist_ok=True)
    
    file_path = os.path.join(documents_path, file.filename)
    
    # Save file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Create document record
    doc_record = DocumentModel(
        filename=file.filename,
        file_path=file_path,
        file_type=file.filename.split(".")[-1],
        status="pending"
    )
    db.add(doc_record)
    db.commit()
    
    return DocumentUploadResponse(
        filename=file.filename,
        status="uploaded",
        chunks_created=0
    )


@router.post("/documents/index")
async def index_documents(db: Session = Depends(get_db)):
    """
    Index all uploaded documents.
    """
    # Load and split documents
    documents = load_documents()
    chunks = split_documents(documents)
    
    # Add to vector store
    if chunks:
        add_documents_to_vectorstore(chunks)
    
    # Update document records
    db.query(DocumentModel).update({
        DocumentModel.status: "indexed",
        DocumentModel.chunk_count: len(chunks),
        DocumentModel.file_size: len(documents)
    })
    db.commit()
    
    # Get stats
    stats = get_collection_stats()
    
    return {
        "status": "completed",
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "vectorstore_count": stats.get("document_count", 0)
    }


@router.get("/documents", response_model=List[DocumentUploadResponse])
async def list_documents(db: Session = Depends(get_db)):
    """
    List all indexed documents.
    """
    docs = db.query(DocumentModel).all()
    return [
        DocumentUploadResponse(
            filename=doc.filename,
            status=doc.status,
            chunks_created=doc.chunk_count
        )
        for doc in docs
    ]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate = None,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    """
    title = request.title if request else "New Conversation"
    conversation = Conversation(title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List all conversations.
    """
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Conversation).count()
    
    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len(c.messages)
            )
            for c in conversations
        ],
        total=total
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Remove chain from memory
    if conversation_id in conversation_chains:
        del conversation_chains[conversation_id]
    
    db.delete(conversation)
    db.commit()
    
    return {"status": "deleted"}


@router.get("/search")
async def search_documents(query: str, k: int = 5):
    """
    Search for similar documents.
    """
    results = similarity_search(query, k=k)
    
    return {
        "query": query,
        "results": [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in results
        ]
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    stats = get_collection_stats()
    return {
        "status": "healthy",
        "vectorstore_documents": stats.get("document_count", 0)
    }

