"""
RAG Service: Chunking → Embeddings → Qdrant storage + semantic search + reranking.
Uses local sentence-transformers by default (no API key needed).
"""
from __future__ import annotations

import uuid
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings

# ── Text Splitter ─────────────────────────────────────────────────────────────
# Financial documents need larger chunks to preserve context
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " "],
)

# ── Embedding Model (local, free) ─────────────────────────────────────────────
_embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# ── Qdrant Client ─────────────────────────────────────────────────────────────
_qdrant = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def _ensure_collection():
    """Create Qdrant collection if it doesn't exist."""
    existing = [c.name for c in _qdrant.get_collections().collections]
    if settings.QDRANT_COLLECTION not in existing:
        _qdrant.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


# ── Public API ────────────────────────────────────────────────────────────────

def index_document(
    document_id: int,
    title: str,
    company_name: str,
    document_type: str,
    content_text: str,
) -> int:
    """
    Split text → embed → store in Qdrant.
    Returns number of chunks stored.
    """
    _ensure_collection()

    chunks = _splitter.split_text(content_text)
    if not chunks:
        return 0

    vectors = _embeddings.embed_documents(chunks)

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "title": title,
                    "company_name": company_name,
                    "document_type": document_type,
                    "chunk_index": i,
                    "chunk_text": chunk,
                },
            )
        )

    _qdrant.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    return len(chunks)


def remove_document(document_id: int) -> bool:
    """Delete all vectors for a document from Qdrant."""
    _ensure_collection()
    _qdrant.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
    )
    return True


def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Full RAG retrieval pipeline:
      query → embed → vector search (top 20) → rerank → top_k results
    """
    _ensure_collection()

    query_vector = _embeddings.embed_query(query)

    # Retrieve top 20 candidates
    hits = _qdrant.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=20,
        with_payload=True,
    )

    if not hits:
        return []

    # Rerank using cross-encoder style scoring
    # Simple financial keyword boosting reranker
    reranked = _rerank(query, hits)

    results = []
    for hit in reranked[:top_k]:
        results.append(
            {
                "document_id": hit.payload["document_id"],
                "document_title": hit.payload["title"],
                "company_name": hit.payload["company_name"],
                "document_type": hit.payload["document_type"],
                "chunk_text": hit.payload["chunk_text"],
                "score": round(hit.score, 4),
            }
        )
    return results


def get_document_context(document_id: int) -> List[str]:
    """Retrieve all stored chunks for a given document, ordered by chunk_index."""
    _ensure_collection()

    results, _ = _qdrant.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
        limit=500,
        with_payload=True,
        with_vectors=False,
    )

    # Sort by chunk index
    results.sort(key=lambda r: r.payload.get("chunk_index", 0))
    return [r.payload["chunk_text"] for r in results]


# ── Reranker ──────────────────────────────────────────────────────────────────

# Financial domain keywords for relevance boosting
_FINANCIAL_TERMS = {
    "revenue", "profit", "loss", "debt", "asset", "liability", "equity",
    "cash flow", "ebitda", "margin", "ratio", "risk", "audit", "balance",
    "income", "expense", "forecast", "budget", "investment", "dividend",
    "compliance", "tax", "interest", "capital", "funding", "valuation",
}


def _rerank(query: str, hits) -> list:
    """
    Simple keyword-overlap reranker for financial relevance.
    Boosts chunks that share financial terms with the query.
    In production: replace with a cross-encoder model like
    cross-encoder/ms-marco-MiniLM-L-6-v2
    """
    query_tokens = set(query.lower().split())
    query_financial = query_tokens & _FINANCIAL_TERMS

    scored = []
    for hit in hits:
        chunk_tokens = set(hit.payload["chunk_text"].lower().split())
        chunk_financial = chunk_tokens & _FINANCIAL_TERMS

        # Overlap between query financial terms and chunk financial terms
        overlap = len(query_financial & chunk_financial)
        boost = 0.05 * overlap  # small positive boost per matching term

        scored.append((hit, hit.score + boost))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored]
