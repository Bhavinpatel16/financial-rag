import os
from pathlib import Path
from pypdf import PdfReader
from fastapi import UploadFile
from app.core.config import settings


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Text extraction failed: {e}]"


async def save_upload_file(upload_file: UploadFile, document_id: int) -> tuple[str, int]:
    """Save uploaded file to disk. Returns (file_path, file_size)."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = f"doc_{document_id}_{upload_file.filename.replace(' ', '_')}"
    file_path = upload_dir / safe_name

    content = await upload_file.read()
    file_size = len(content)

    # Check size limit
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise ValueError(f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB allowed.")

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path), file_size


def delete_file(file_path: str) -> bool:
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False
