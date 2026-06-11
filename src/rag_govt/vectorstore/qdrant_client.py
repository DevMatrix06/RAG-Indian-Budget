"""Qdrant collection management and vector upsert/search helpers."""
from __future__ import annotations

import uuid

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag_govt.ingestion.chunker import Chunk

_UPSERT_BATCH = 256


class QdrantStore:
    def __init__(
        self,
        collection: str,
        dim: int,
        path: str = "",
        host: str = "localhost",
        port: int = 6333,
    ) -> None:
        self.collection = collection
        self.dim = dim
        # Local file mode when path is given; server mode otherwise.
        self._client = QdrantClient(path=path) if path else QdrantClient(host=host, port=port)

    def ensure_collection(self) -> None:
        """Create the collection with cosine similarity if it does not exist."""
        if not self._client.collection_exists(self.collection):
            self._client.create_collection(
                self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )

    def upsert(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        """Upsert in batches to avoid oversized gRPC payloads."""
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i].tolist(),
                payload={
                    "text": chunk.text,
                    "source": chunk.source,
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        for start in range(0, len(points), _UPSERT_BATCH):
            self._client.upsert(
                collection_name=self.collection,
                points=points[start : start + _UPSERT_BATCH],
            )

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[dict]:
        """Return top_k results as payload dicts with an added 'score' key."""
        result = self._client.query_points(
            collection_name=self.collection,
            query=query_vector.tolist(),
            limit=top_k,
        )
        return [{**hit.payload, "score": hit.score} for hit in result.points]
