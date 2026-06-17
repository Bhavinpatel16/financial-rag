from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentType


class DocumentRead(BaseModel):
    id: int
    title: str
    company_name: str
    document_type: DocumentType
    file_name: str
    file_size: Optional[int]
    uploaded_by: Optional[int]
    created_at: datetime
    is_indexed: str

    class Config:
        from_attributes = True


class DocumentSearch(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    document_type: Optional[DocumentType] = None


# ── RAG Schemas ─────────────────────────────────────────────────────────────
class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class RAGChunkResult(BaseModel):
    document_id: int
    document_title: str
    company_name: str
    document_type: str
    chunk_text: str
    score: float


class RAGSearchResponse(BaseModel):
    query: str
    results: List[RAGChunkResult]
    total_results: int


class RAGContextResponse(BaseModel):
    document_id: int
    title: str
    company_name: str
    chunks: List[str]
    total_chunks: int
