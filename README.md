# RAG — Indian Government Budget Documents

> **Domain-agnostic RAG pipeline over Indian government budget documents. Swap the corpus for any knowledge domain.**

Retrieval-augmented generation system that indexes dense PDF corpora and answers natural-language questions with cited sources. Built as a portfolio project demonstrating an end-to-end production-shaped RAG stack — ingestion, embedding, vector search, generation, and quantitative eval.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Ingestion Pipeline                       │
│                                                                  │
│  PDF files                                                       │
│  data/pdfs/  ──► PyMuPDF ──► Chunker ──► BGE Encoder ──► Qdrant │
│                  (loader)   (512-word    (384-dim       (local   │
│                              sliding     embeddings)    file     │
│                              window)                    store)   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                          Query Pipeline                          │
│                                                                  │
│  User question                                                   │
│      │                                                           │
│      ▼                                                           │
│  BGE Encoder  ──► Qdrant top-k ──► Retrieved chunks             │
│  (query prefix)   cosine search       │                          │
│                                       ▼                          │
│                             Gemini 2.5 Flash ──► Answer + sources │
│                             (streamed; prompt                    │
│                              cites PDF + page)                   │
└──────────────────────────────────────────────────────────────────┘

             FastAPI  (POST /ingest,  POST /query)
```

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **API** | FastAPI + Uvicorn | Async, lifespan resource management |
| **PDF parsing** | PyMuPDF (`fitz`) | Fast text extraction, handles dense govt PDFs |
| **Chunking** | Sliding window (512 words, 64 overlap) | Word-level, not character-level |
| **Embeddings** | `BAAI/bge-small-en-v1.5` (384-dim) | BGE query prefix applied at retrieval time |
| **Vector store** | Qdrant | Local file mode (no Docker needed for dev) |
| **Generation** | Google Gemini 2.5 Flash (`google-genai`) | Free-tier API key via Google AI Studio; token streaming |
| **Config** | `pydantic-settings` + `.env` | Type-safe, all values overridable |
| **Package mgr** | `uv` | Fast, reproducible, `pyproject.toml`-native |
| **Eval** | Custom hit-rate harness | 20-question gold set, substring match |

---

## Corpus

5 Indian Union Budget 2026–27 documents (~1,075 chunks after ingestion):

| File | Description |
|---|---|
| `allsbe.pdf` | Statement of Budget Estimates — all ministries |
| `bag6.pdf` | Budget at a Glance (English) |
| `bag7.pdf` | Budget at a Glance (Hindi) |
| `Key_to_Budget_Document_2026.pdf` | Guide to all budget documents |
| `Finance_Bill.pdf` | Finance Bill 2026 |

---

## Retrieval Eval

Evaluated against a **20-question gold set** spanning fiscal deficit, capital expenditure, specific ministry allocations, legislative documents, and scheme frameworks.

| Metric | Value |
|---|---|
| **Hit rate** | **14 / 20 (70%)** |
| **Avg top-1 similarity** | **0.772** |
| **Avg top-5 mean similarity** | **0.748** |
| **Questions scoring below 0.65** | **0** |

Hit = the expected answer phrase found in top-5 retrieved chunks (cosine similarity, BGE-normalised).  
Zero low-scorers means the model never returns semantically unrelated chunks — every miss is a rank > 5 miss, not a semantic failure.

→ **[Full per-question results](evals/results.md)**

---

## Quickstart

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Google Gemini API key (free) — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Install

```bash
git clone <repo>
cd RAG_GOVT_INFO
uv sync
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY
```

### 3. Ingest PDFs

Drop your PDF files into `data/pdfs/`, then:

```bash
uv run python scripts/ingest_pdfs.py
```

Embeddings and vectors are stored in `./qdrant_data/` (local file mode — no Docker required).  
To use a self-hosted Qdrant server instead, set `QDRANT_PATH=` (empty) and configure `QDRANT_HOST`/`QDRANT_PORT` in `.env`.

### 4. Start the API

```bash
uv run uvicorn rag_govt.api.main:app --reload
```

Interactive docs: **http://localhost:8000/docs**

### 5. Query (API)

```bash
# Standard JSON response
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital expenditure for 2026-27?", "top_k": 5}'

# Streaming (SSE) — sources first, then answer tokens as they generate
curl -N -X POST http://localhost:8000/query/stream/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital expenditure for 2026-27?", "top_k": 5}'
```

### 5b. Web UI (optional)

A React + Vite frontend lives in `frontend/` — a streaming search interface with live token rendering, source citations, and a Three.js particle background.

The backend and frontend run as two separate processes, so use **two terminals** and keep both open:

**Terminal 1 — API** (must stay running; the local Qdrant file is locked to this one process):

```bash
# from the repo root
uv run uvicorn rag_govt.api.main:app --host 0.0.0.0 --port 8000 --reload
```

> On Windows PowerShell, set `$env:PYTHONUTF8 = "1"` first so Devanagari/₹ output doesn't crash the console.

**Terminal 2 — frontend:**

```bash
cd frontend
npm install        # first time only
npm run dev        # http://localhost:5173 (Vite proxies API calls to :8000)
```

Then open **http://localhost:5173**.

> **Troubleshooting:** if startup fails with `portalocker … AlreadyLocked` / "Storage folder is already accessed by another instance", a previous API process is still holding the Qdrant lock — kill it first (`Get-Process python | Stop-Process -Force` on Windows) and restart.

### 6. Ingest via API

```bash
curl -X POST http://localhost:8000/ingest/ \
  -F "file=@data/pdfs/myfile.pdf"
```

### 7. Run eval

```bash
# Stop the API server first (local Qdrant allows only one reader at a time)
uv run python evals/ragas_eval.py
# Results written to evals/results.md
```

---

## Project Structure

```
src/rag_govt/
├── config.py           # pydantic-settings, reads .env
├── ingestion/
│   ├── loader.py       # PDF → page dicts via PyMuPDF
│   └── chunker.py      # sliding-window word chunker
├── embeddings/
│   └── encoder.py      # BGE wrapper, lazy model load
├── vectorstore/
│   └── qdrant_client.py # upsert / query_points helpers
├── retrieval/
│   └── retriever.py    # encode query → vector search
├── generation/
│   └── generator.py    # Gemini API call, lazy import
└── api/
    ├── main.py          # FastAPI app + lifespan resources
    └── routes/
        ├── ingest.py    # POST /ingest
        └── query.py     # POST /query, POST /query/stream (SSE)

scripts/
└── ingest_pdfs.py       # one-shot bulk ingestion CLI

evals/
├── ragas_eval.py        # 20-question retrieval eval harness
└── results.md           # latest eval output

frontend/                # React + Vite + Tailwind streaming UI
├── src/
│   ├── App.tsx          # query state machine, SSE consumption
│   ├── lib/api.ts       # streaming fetch + SSE parser
│   └── components/      # SearchBar, AnswerCard, CitationChip, ParticleBackground
└── vite.config.ts       # dev proxy → :8000
```

---

## Known Limitations & Next Steps

### Retrieval quality
- **Expand `top_k` to 8–10** — all 6 eval misses are rank > 5 misses, not semantic failures. Raising `top_k` is projected to push hit rate to ~85% with no other changes.
- **Section-aware chunking** — budget PDFs have dense numeric tables where row context is split across chunks. Chunking at section boundaries (detecting table headers) would keep row + header together, fixing most numeric lookup misses.
- **Cross-encoder reranking** — add a lightweight cross-encoder (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) as a second-stage ranker over the top-20 BGE candidates. Expected +5–10% hit rate.

### Ingestion
- **Deduplication** — re-running the ingest script adds duplicate vectors. A content hash stored in the Qdrant payload would let the upsert skip already-indexed chunks.
- **OCR support** — scanned PDFs (image-only pages) are silently skipped. Adding `pytesseract` as a fallback would handle older government documents.

### Production hardening
- **Switch to Qdrant server** — the local file mode serialises all reads/writes; concurrent API requests will queue (and the eval can't run while the API holds the lock). Use the `docker-compose.yml` for a proper server.
- **RAGAS evals** — the current eval is a hand-rolled hit-rate harness. Integrating [RAGAS](https://docs.ragas.io) would add faithfulness and answer relevancy metrics.
- **Retry on rate limits** — the free Gemini tier has per-minute quotas; add exponential-backoff retry on `429` so bursts of queries degrade gracefully instead of erroring.
