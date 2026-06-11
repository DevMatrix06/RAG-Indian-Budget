"""One-shot CLI script: ingest all PDFs in data/pdfs/ into Qdrant.

Usage:
    uv run python scripts/ingest_pdfs.py
"""
from pathlib import Path

from rag_govt.config import settings
from rag_govt.embeddings.encoder import Encoder
from rag_govt.ingestion.chunker import chunk_pages
from rag_govt.ingestion.loader import load_directory
from rag_govt.vectorstore.qdrant_client import QdrantStore

PDF_DIR = Path(__file__).parent.parent / "data" / "pdfs"


def main() -> None:
    encoder = Encoder(settings.embedding_model)
    store = QdrantStore(
        collection=settings.qdrant_collection,
        dim=settings.embedding_dim,
        path=settings.qdrant_path,
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )
    store.ensure_collection()

    print(f"Loading PDFs from {PDF_DIR} ...")
    pages = load_directory(PDF_DIR)
    if not pages:
        print(f"No PDFs found. Drop files into {PDF_DIR} and re-run.")
        return

    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    print(f"Embedding {len(chunks)} chunks ...")
    vectors = encoder.encode([c.text for c in chunks], batch_size=64)

    print("Upserting into Qdrant ...")
    store.upsert(chunks, vectors)
    print(f"Done — {len(chunks)} chunks indexed into '{settings.qdrant_collection}'.")


if __name__ == "__main__":
    main()
