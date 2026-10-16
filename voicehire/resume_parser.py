from __future__ import annotations

from io import BytesIO


def extract_resume_text(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "txt":
        return content.decode("utf-8", errors="replace")
    if suffix == "pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == "docx":
        from docx import Document

        doc = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    raise ValueError("Supported resume formats are PDF, DOCX, and TXT.")
