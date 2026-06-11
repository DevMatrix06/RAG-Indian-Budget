"""Load raw text from PDF files using pymupdf."""
from pathlib import Path

import fitz  # pymupdf


def load_pdf(path: Path) -> list[dict]:
    """Return a list of {page: int, text: str, source: str} dicts, one per page."""
    pages = []
    with fitz.open(str(path)) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page": page_num, "text": text, "source": path.name})
    return pages


def load_directory(pdf_dir: Path) -> list[dict]:
    """Load all PDFs in a directory, tagging each page with its source filename."""
    pages = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        pages.extend(load_pdf(pdf_path))
    return pages
