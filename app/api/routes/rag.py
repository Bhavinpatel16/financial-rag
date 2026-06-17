from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import RAGSearchRequest, RAGSearchResponse, RAGChunkResult, RAGContextResponse
from app.core.security import get_current_user
from app.services import rag_service

router = APIRouter(prefix="/rag", tags=["RAG / Semantic Search"])


@router.post("/index-document/{document_id}")
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate embeddings for a document and store in Qdrant.
    Requires Admin or Analyst role.
    """
    _require_roles(current_user, ["admin", "analyst"])

    doc = _get_doc_or_404(document_id, db)

    if not doc.content_text or len(doc.content_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Document has insufficient text content for indexing",
        )

    try:
        chunk_count = rag_service.index_document(
            document_id=doc.id,
            title=doc.title,
            company_name=doc.company_name,
            document_type=doc.document_type.value,
            content_text=doc.content_text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

    doc.is_indexed = "true"
    db.commit()

    return {
        "message": "Document indexed successfully",
        "document_id": document_id,
        "chunks_stored": chunk_count,
    }


@router.delete("/remove-document/{document_id}")
def remove_document_embeddings(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a document's embeddings from the vector database."""
    _require_roles(current_user, ["admin"])
    doc = _get_doc_or_404(document_id, db)

    try:
        rag_service.remove_document(document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Removal failed: {e}")

    doc.is_indexed = "false"
    db.commit()

    return {"message": "Embeddings removed", "document_id": document_id}


@router.post("/search", response_model=RAGSearchResponse)
def semantic_search(
    payload: RAGSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Perform semantic search over all indexed financial documents.

    Pipeline: query → embedding → vector search (top 20) → rerank → top_k results
    """
    try:
        results = rag_service.semantic_search(query=payload.query, top_k=payload.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    chunk_results = [RAGChunkResult(**r) for r in results]

    return RAGSearchResponse(
        query=payload.query,
        results=chunk_results,
        total_results=len(chunk_results),
    )


@router.get("/context/{document_id}", response_model=RAGContextResponse)
def get_document_context(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all stored text chunks for a specific document."""
    doc = _get_doc_or_404(document_id, db)

    if doc.is_indexed != "true":
        raise HTTPException(status_code=400, detail="Document is not indexed yet")

    try:
        chunks = rag_service.get_document_context(document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {e}")

    return RAGContextResponse(
        document_id=doc.id,
        title=doc.title,
        company_name=doc.company_name,
        chunks=chunks,
        total_chunks=len(chunks),
    )


def _get_doc_or_404(document_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def _require_roles(user: User, allowed: list):
    role_names = [r.name.lower() for r in user.roles]
    if not any(r in allowed for r in role_names):
        raise HTTPException(status_code=403, detail=f"Requires roles: {allowed}")
