"""
Main application entry point for the RAG Chat Bot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.chat import router as chat_router
from backend.db.session import init_db
from backend.core.config import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"Application started: {settings.app_name}")
    
    yield
    print("Application is shutting down...")


# Create FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description="A RAG-powered chat bot that answers questions based on your documents",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }


