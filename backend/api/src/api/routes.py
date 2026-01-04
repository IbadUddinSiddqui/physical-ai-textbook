from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import asyncio
import os
from dotenv import load_dotenv
from ..models.content_models import SearchRequest, SearchResponse, ChunkRequest, ContentChunkResponse
from ..rag.rag_service import RAGService
from ..chatbot.gemini_chatbot import GeminiChatbot

# Load environment variables from backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend', '.env'))

router = APIRouter()

# Global RAG service instance
rag_service = RAGService()

# Global chatbot instance
chatbot = None

@router.on_event("startup")
async def startup_event():
    await rag_service.initialize()
    global chatbot
    chatbot = GeminiChatbot(rag_service)

@router.on_event("shutdown")
async def shutdown_event():
    await rag_service.close()

@router.post("/chunks/process", response_model=ContentChunkResponse)
async def process_content_chunk(chunk_request: ChunkRequest):
    """Process and store a content chunk in the RAG system"""
    try:
        result = await rag_service.process_and_store_content(
            chunk_request.chapter_id,
            chunk_request.content
        )

        if result["success"]:
            return ContentChunkResponse(
                chunk_id=result["chapter_id"],
                chapter_id=result["chapter_id"],
                content_preview=chunk_request.content[:100] + "..." if len(chunk_request.content) > 100 else chunk_request.content,
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing content: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_content(search_request: SearchRequest):
    """Search for content in the RAG system"""
    try:
        results = await rag_service.search_content(search_request.query, search_request.limit)

        return SearchResponse(
            results=results,
            query=search_request.query,
            limit=search_request.limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")

@router.post("/chat", response_model=Dict)
async def chat_with_textbook(query: str):
    """Chat with the textbook using RAG-augmented Gemini"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot service not initialized")

        result = await chatbot.get_contextual_response(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/health")
async def api_health():
    """Health check for the RAG API"""
    return {"status": "healthy", "service": "RAG API"}

# Include routes in main app
def include_rag_routes(app):
    app.include_router(router, prefix="/api/v1", tags=["RAG"])