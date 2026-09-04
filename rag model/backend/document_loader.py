from pathlib import Path
import fitz
from docx import Document


def load_pdf(file_path):
    documents = []

    pdf = fitz.open(file_path)

    for page_number, page in enumerate(pdf, start=1):

        text = page.get_text("text")

        if text and text.strip():

            documents.append({
                "text": text.strip(),
                "source": file_path,
                "page": page_number
            })

    pdf.close()

    return documents


def load_docx(file_path):

    doc = Document(file_path)

    paragraphs = []

    for paragraph in doc.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)

    return [{
        "text": full_text,
        "source": file_path,
        "page": None
    }]


def load_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return [{
        "text": text,
        "source": file_path,
        "page": None
    }]


def load_document(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".docx":
        return load_docx(file_path)

    elif extension == ".txt":
        return load_txt(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )