from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages_text: list[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized_text = " ".join(text.split())
        if normalized_text:
            pages_text.append(f"[Page {page_number}] {normalized_text}")

    return "\n\n".join(pages_text).strip()
