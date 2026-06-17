from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.document import Document, DocumentType
from app.models.user import User
from app.schemas.document import DocumentRead, DocumentSearch
from app.core.security import get_current_user
from app.services.file_service import save_upload_file, extract_text_from_pdf, delete_file

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a financial document (PDF). Requires 'documents:upload' permission."""
    _check_permission(current_user, ["admin", "analyst"])

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Create DB record first to get the ID
    doc = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_name=file.filename,
        file_path="",  # filled in after save
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        file_path, file_size = await save_upload_file(file, doc.id)
    except ValueError as e:
        db.delete(doc)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))

    # Extract text from PDF
    content_text = extract_text_from_pdf(file_path)

    doc.file_path = file_path
    doc.file_size = file_size
    doc.content_text = content_text
    db.commit()
    db.refresh(doc)

    return doc


@router.get("", response_model=List[DocumentRead])
def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all documents. Clients see only their company's documents."""
    query = db.query(Document)

    # Clients can only see documents uploaded by themselves
    role_names = [r.name.lower() for r in current_user.roles]
    if "client" in role_names and "admin" not in role_names:
        query = query.filter(Document.uploaded_by == current_user.id)

    return query.offset(skip).limit(limit).all()


@router.get("/search", response_model=List[DocumentRead])
def search_documents(
    title: Optional[str] = Query(None),
    company_name: Optional[str] = Query(None),
    document_type: Optional[DocumentType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search documents by metadata fields."""
    query = db.query(Document)

    if title:
        query = query.filter(Document.title.ilike(f"%{title}%"))
    if company_name:
        query = query.filter(Document.company_name.ilike(f"%{company_name}%"))
    if document_type:
        query = query.filter(Document.document_type == document_type)

    return query.limit(50).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single document by ID."""
    doc = _get_doc_or_404(document_id, db)
    _check_doc_access(current_user, doc)
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document (Admin only)."""
    _check_permission(current_user, ["admin"])
    doc = _get_doc_or_404(document_id, db)

    # Remove embeddings from vector DB if indexed
    if doc.is_indexed == "true":
        try:
            from app.services.rag_service import remove_document
            remove_document(doc.id)
        except Exception:
            pass  # Don't fail delete if Qdrant is unavailable

    delete_file(doc.file_path)
    db.delete(doc)
    db.commit()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_doc_or_404(document_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def _check_permission(user: User, allowed_roles: list):
    role_names = [r.name.lower() for r in user.roles]
    if not any(r in allowed_roles for r in role_names):
        raise HTTPException(
            status_code=403,
            detail=f"Requires one of roles: {allowed_roles}",
        )


def _check_doc_access(user: User, doc: Document):
    role_names = [r.name.lower() for r in user.roles]
    if "admin" in role_names or "analyst" in role_names or "auditor" in role_names:
        return  # full access
    # Clients can only see their own uploads
    if doc.uploaded_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
