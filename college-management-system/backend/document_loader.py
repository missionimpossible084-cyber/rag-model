from pathlib import Path

import pymupdf
from docx import Document


def load_pdf(file_path: str):
    """
    Load text from PDF.
    """

    documents = []

    pdf = pymupdf.open(file_path)

    for page_number, page in enumerate(pdf):
        text = page.get_text("text").strip()

        if text:
            documents.append(
                {
                    "text": text,
                    "source": Path(file_path).name,
                    "page": page_number + 1,
                }
            )

    pdf.close()

    return documents


def load_docx(file_path: str):
    """
    Load text from DOCX.
    """

    document = Document(file_path)

    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    full_text = "\n".join(text_parts)

    if not full_text:
        return []

    return [
        {
            "text": full_text,
            "source": Path(file_path).name,
            "page": None,
        }
    ]


def load_txt(file_path: str):
    """
    Load TXT file.
    """

    path = Path(file_path)

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    ).strip()

    if not text:
        return []

    return [
        {
            "text": text,
            "source": path.name,
            "page": None,
        }
    ]


def load_document(file_path: str):
    """
    Automatically select loader based on extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".docx":
        return load_docx(file_path)

    if extension == ".txt":
        return load_txt(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )
