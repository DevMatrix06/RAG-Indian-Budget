"""FastAPI application factory with lifespan resource management."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_govt.config import settings
from rag_govt.embeddings.encoder import Encoder
from rag_govt.generation.generator import Generator
from rag_govt.retrieval.retriever import Retriever
from rag_govt.vectorstore.qdrant_client import QdrantStore


# Shared resources — populated during lifespan startup
_resources: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    encoder = Encoder(settings.embedding_model)
    store = QdrantStore(
        collection=settings.qdrant_collection,
        dim=settings.embedding_dim,
        path=settings.qdrant_path,
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )
    store.ensure_collection()
    _resources.update(
        {
            "encoder": encoder,
            "store": store,
            "retriever": Retriever(encoder, store),
            "generator": Generator(settings.google_api_key, settings.google_model),
        }
    )
    yield
    _resources.clear()


def get_encoder() -> Encoder:
    return _resources["encoder"]


def get_store() -> QdrantStore:
    return _resources["store"]


def get_retriever() -> Retriever:
    return _resources["retriever"]


def get_generator() -> Generator:
    return _resources["generator"]


app = FastAPI(title="RAG Govt Schemes API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from rag_govt.api.routes import ingest, query  # noqa: E402 — after app is defined

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(query.router, prefix="/query", tags=["query"])
