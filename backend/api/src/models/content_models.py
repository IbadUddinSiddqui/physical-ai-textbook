from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class ContentChunk(BaseModel):
    """Model for content chunks"""
    chunk_id: str
    chapter_id: str
    content: str
    metadata: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EmbeddingMetadata(BaseModel):
    """Model for embedding metadata"""
    id: Optional[int] = None
    chunk_id: str
    embedding_id: str
    content_hash: str
    chapter_title: Optional[str] = None
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    source_file: Optional[str] = None
    created_at: Optional[datetime] = None

class ChunkRequest(BaseModel):
    """Request model for chunking content"""
    content: str
    chunk_size: int = 1000
    overlap: int = 100
    chapter_id: str

class SearchRequest(BaseModel):
    """Request model for search functionality"""
    query: str
    limit: int = 5

class SearchResponse(BaseModel):
    """Response model for search results"""
    results: List[Dict]
    query: str
    limit: int

class ContentChunkResponse(BaseModel):
    """Response model for content chunk operations"""
    chunk_id: str
    chapter_id: str
    content_preview: str
    success: bool
    message: str