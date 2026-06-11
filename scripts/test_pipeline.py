import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
print("step 1: config", flush=True)
from rag_govt.config import settings

print("step 2: encoder", flush=True)
from rag_govt.embeddings.encoder import Encoder
encoder = Encoder(settings.embedding_model)

print("step 3: qdrant", flush=True)
from rag_govt.vectorstore.qdrant_client import QdrantStore
store = QdrantStore(
    collection=settings.qdrant_collection,
    dim=settings.embedding_dim,
    path=settings.qdrant_path,
)

print("step 4: retriever", flush=True)
from rag_govt.retrieval.retriever import Retriever
retriever = Retriever(encoder, store)

print("step 5: generator (lazy client)", flush=True)
from rag_govt.generation.generator import Generator
generator = Generator(settings.google_api_key, settings.google_model)

q = "What is the total budget allocation for infrastructure in this year Indian budget?"

print("step 6: retrieve", flush=True)
chunks = retriever.retrieve(q, top_k=5)
print(f"Got {len(chunks)} chunks", flush=True)
for c in chunks:
    print(f"  [{c['score']:.3f}] {c['source']} p{c['page']}: {c['text'][:100]}", flush=True)

print("\nstep 7: generate", flush=True)
answer = generator.generate(q, chunks)
print("\nANSWER:\n", answer, flush=True)
