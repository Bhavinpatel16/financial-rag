from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class DocumentType(str, enum.Enum):
    invoice = "invoice"
    report = "report"
    contract = "contract"
    agreement = "agreement"
    other = "other"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company_name = Column(String, nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer)  # bytes
    content_text = Column(Text)  # extracted text
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Whether embeddings have been generated
    is_indexed = Column(String, default="false")

    uploader = relationship("User", back_populates="documents")
