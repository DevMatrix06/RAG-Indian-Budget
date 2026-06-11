"""Orchestrate encode → search → return ranked context chunks."""
from __future__ import annotations

from rag_govt.embeddings.encoder import Encoder
from rag_govt.vectorstore.qdrant_client import QdrantStore


class Retriever:
    def __init__(self, encoder: Encoder, store: QdrantStore, top_k: int = 5) -> None:
        self.encoder = encoder
        self.store = store
        self.top_k = top_k

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        """Encode query, search Qdrant, return ranked payload dicts."""
        vector = self.encoder.encode_query(query)
        return self.store.search(vector, top_k=top_k if top_k is not None else self.top_k)
