"""Thin wrapper around sentence-transformers for batch encoding."""
from __future__ import annotations

import numpy as np

# BGE retrieval models require this prefix on query strings, not on passages.
_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class Encoder:
    """Lazy-loads the model on first use to avoid startup cost."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _load(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """Return float32 array of shape (len(texts), embedding_dim)."""
        if self._model is None:
            self._load()
        return self._model.encode(  # type: ignore[union-attr]
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query with the BGE prefix. Returns 1-D vector."""
        return self.encode([_BGE_QUERY_PREFIX + query])[0]
