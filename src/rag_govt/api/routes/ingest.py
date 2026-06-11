"""POST /ingest — upload a PDF and add its chunks to Qdrant."""
import asyncio
import tempfile
from functools import partial
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from rag_govt.api.main import get_encoder, get_store
from rag_govt.config import settings
from rag_govt.embeddings.encoder import Encoder
from rag_govt.ingestion.chunker import chunk_pages
from rag_govt.ingestion.loader import load_pdf
from rag_govt.vectorstore.qdrant_client import QdrantStore

router = APIRouter()


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int


@router.post("/", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile,
    encoder: Encoder = Depends(get_encoder),
    store: QdrantStore = Depends(get_store),
) -> IngestResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    loop = asyncio.get_running_loop()
    try:
        pages = await loop.run_in_executor(None, partial(load_pdf, tmp_path))
    finally:
        tmp_path.unlink(missing_ok=True)

    if not pages:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF.")

    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    vectors = await loop.run_in_executor(
        None, partial(encoder.encode, [c.text for c in chunks])
    )
    await loop.run_in_executor(None, partial(store.upsert, chunks, vectors))

    return IngestResponse(filename=file.filename or "unknown.pdf", chunks_added=len(chunks))
