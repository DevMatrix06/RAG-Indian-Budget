"""
Retrieval quality evaluation — 20-question gold set.

Metrics
-------
hit_rate   : fraction of questions where the expected answer phrase is found in top-5 chunks
avg_score  : mean top-1 similarity score across all questions
low_scorers: questions where max(top-5 score) < LOW_SCORE_THRESHOLD

Run:  uv run python evals/ragas_eval.py
Note: stop the API server first — local Qdrant only allows one reader at a time.
"""
import io
import sys
from datetime import date
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from rag_govt.config import settings
from rag_govt.embeddings.encoder import Encoder
from rag_govt.retrieval.retriever import Retriever
from rag_govt.vectorstore.qdrant_client import QdrantStore

LOW_SCORE_THRESHOLD = 0.65

# ---------------------------------------------------------------------------
# Gold eval set — question + a distinctive phrase expected in a top-5 chunk.
# answer_contains is a case-insensitive substring match.
# ---------------------------------------------------------------------------
EVAL_SET = [
    {
        "id": 1, "topic": "Total Expenditure",
        "question": "What is the Grand Total expenditure of Government of India for 2026-27 Budget Estimates?",
        "answer_contains": "5347315",
    },
    {
        "id": 2, "topic": "Capital Expenditure",
        "question": "What is the effective capital expenditure of the Government including grants for capital assets in 2026-27?",
        "answer_contains": "1714523",
    },
    {
        "id": 3, "topic": "Budget Documents",
        "question": "What documents are presented to Parliament along with the Finance Minister's Budget Speech?",
        "answer_contains": "Annual Financial Statement",
    },
    {
        "id": 4, "topic": "Finance Minister",
        "question": "Who presented the Finance Bill 2026 to Parliament?",
        "answer_contains": "Nirmala Sitharaman",
    },
    {
        "id": 5, "topic": "Finance Bill",
        "question": "When was the Finance Bill 2026 introduced in the Lok Sabha?",
        "answer_contains": "1st February, 2026",
    },
    {
        "id": 6, "topic": "Interest Payments",
        "question": "What is the interest payment provision in the 2026-27 Budget Estimates?",
        "answer_contains": "1403971",
    },
    {
        "id": 7, "topic": "Housing & Urban Affairs",
        "question": "What is the total budget allocation for the Ministry of Housing and Urban Affairs in 2026-27?",
        "answer_contains": "85522",
    },
    {
        "id": 8, "topic": "Jal Shakti",
        "question": "What is the total budget provision for the Ministry of Jal Shakti in 2026-27?",
        "answer_contains": "94807",
    },
    {
        "id": 9, "topic": "Centrally Sponsored Schemes",
        "question": "What is the total allocation for Centrally Sponsored Schemes in 2026-27 Budget Estimates?",
        "answer_contains": "548798",
    },
    {
        "id": 10, "topic": "Roads & Bridges",
        "question": "What is the budget provision for Roads and Bridges under Economic Services in 2026-27?",
        "answer_contains": "5144",
    },
    {
        "id": 11, "topic": "Annual Financial Statement",
        "question": "What does the Annual Financial Statement show as mandated under Article 112 of the Constitution?",
        "answer_contains": "receipts and expenditure",
    },
    {
        "id": 12, "topic": "Finance Commission Grants",
        "question": "What is the Finance Commission Grants allocation for states in 2026-27?",
        "answer_contains": "129397",
    },
    {
        "id": 13, "topic": "Output Outcome Framework",
        "question": "What is the Output Outcome Monitoring Framework and which schemes does it cover?",
        "answer_contains": "Output Outcome Monitoring Framework",
    },
    {
        "id": 14, "topic": "FRBM Act",
        "question": "What fiscal policy statements are mandated under the Fiscal Responsibility and Budget Management Act 2003?",
        "answer_contains": "Fiscal Responsibility and Budget Management",
    },
    {
        "id": 15, "topic": "Finance Bill Purpose",
        "question": "What is the stated object and purpose of the Finance Bill 2026?",
        "answer_contains": "financial proposals",
    },
    {
        "id": 16, "topic": "Central Sector Schemes",
        "question": "What is the allocation for Central Sector Schemes and Projects in 2026-27 Budget Estimates?",
        "answer_contains": "1771928",
    },
    {
        "id": 17, "topic": "Renewable Energy",
        "question": "What is the budget allocation for the Ministry of New and Renewable Energy in 2026-27?",
        "answer_contains": "32914",
    },
    {
        "id": 18, "topic": "Labour & Employment",
        "question": "What is the total budget provision for Ministry of Labour and Employment in 2026-27?",
        "answer_contains": "32666",
    },
    {
        "id": 19, "topic": "Expenditure Profile",
        "question": "What information does the Expenditure Profile budget document contain?",
        "answer_contains": "Expenditure Profile",
    },
    {
        "id": 20, "topic": "MSME",
        "question": "What is the budget allocation for the Ministry of Micro, Small and Medium Enterprises in 2026-27?",
        "answer_contains": "24566",
    },
]


def run_eval() -> list[dict]:
    print("Loading encoder and connecting to Qdrant...")
    encoder = Encoder(settings.embedding_model)
    try:
        store = QdrantStore(
            collection=settings.qdrant_collection,
            dim=settings.embedding_dim,
            path=settings.qdrant_path,
        )
    except RuntimeError as e:
        print(f"\nERROR: {e}")
        print("Stop the API server (it holds the Qdrant lock) then re-run.")
        sys.exit(1)

    retriever = Retriever(encoder, store)
    results = []

    for item in EVAL_SET:
        chunks = retriever.retrieve(item["question"], top_k=5)
        max_score = chunks[0]["score"] if chunks else 0.0
        avg_top5 = sum(c["score"] for c in chunks) / len(chunks) if chunks else 0.0
        hit = any(item["answer_contains"].lower() in c["text"].lower() for c in chunks)
        top_source = f"{chunks[0]['source']} p{chunks[0]['page']}" if chunks else "—"
        results.append({
            "id": item["id"],
            "topic": item["topic"],
            "question": item["question"],
            "hit": hit,
            "max_score": max_score,
            "avg_top5": avg_top5,
            "top_source": top_source,
            "low": max_score < LOW_SCORE_THRESHOLD,
        })
        status = "HIT " if hit else "MISS"
        flag = " ⚠ LOW" if max_score < LOW_SCORE_THRESHOLD else ""
        print(f"  [{item['id']:02d}] {status} | {max_score:.3f} | {item['topic']}{flag}")

    return results


def format_markdown(results: list[dict]) -> str:
    hit_rate = sum(r["hit"] for r in results) / len(results) * 100
    avg_score = sum(r["max_score"] for r in results) / len(results)
    avg_avg5 = sum(r["avg_top5"] for r in results) / len(results)
    low = [r for r in results if r["low"]]
    hits = sum(r["hit"] for r in results)

    lines = [
        f"# Retrieval Eval Results",
        f"",
        f"**Date:** {date.today()}  ",
        f"**Collection:** `{settings.qdrant_collection}`  ",
        f"**Embedding model:** `{settings.embedding_model}`  ",
        f"**Eval set:** 20 questions, hit = answer phrase found in top-5 chunks  ",
        f"**Low-score threshold:** {LOW_SCORE_THRESHOLD}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Hit rate | **{hits}/20 ({hit_rate:.0f}%)** |",
        f"| Avg top-1 score | **{avg_score:.3f}** |",
        f"| Avg top-5 mean score | **{avg_avg5:.3f}** |",
        f"| Questions below {LOW_SCORE_THRESHOLD} | **{len(low)}** |",
        f"",
        f"## Per-question Results",
        f"",
        f"| # | Topic | Hit | Top-1 Score | Avg Top-5 | Top Source | Flag |",
        f"|---|-------|-----|-------------|-----------|------------|------|",
    ]

    for r in results:
        hit_cell = "✅" if r["hit"] else "❌"
        flag_cell = "⚠ low score" if r["low"] else ""
        lines.append(
            f"| {r['id']} | {r['topic']} | {hit_cell} | {r['max_score']:.3f} "
            f"| {r['avg_top5']:.3f} | {r['top_source']} | {flag_cell} |"
        )

    if low:
        lines += [
            f"",
            f"## Low-Score Questions (< {LOW_SCORE_THRESHOLD})",
            f"",
        ]
        for r in low:
            lines.append(f"- **Q{r['id']} — {r['topic']}:** {r['question']}")
            lines.append(f"  - Top-1 score: {r['max_score']:.3f} | Source: {r['top_source']}")

    lines += [
        f"",
        f"## Notes",
        f"",
        f"- Hit detection uses case-insensitive substring match of a key answer phrase in retrieved chunks.",
        f"- Scores are cosine similarities from `{settings.embedding_model}` (BGE, normalised).",
        f"- A score ≥ 0.65 indicates strong semantic overlap; ≥ 0.70 is high confidence.",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    print(f"\nRunning retrieval eval — {len(EVAL_SET)} questions\n")
    results = run_eval()

    hit_rate = sum(r["hit"] for r in results) / len(results) * 100
    avg_score = sum(r["max_score"] for r in results) / len(results)
    low = [r for r in results if r["low"]]

    print(f"\n{'='*50}")
    print(f"  Hit rate : {sum(r['hit'] for r in results)}/20 ({hit_rate:.0f}%)")
    print(f"  Avg score: {avg_score:.3f}")
    print(f"  Low (<{LOW_SCORE_THRESHOLD}): {len(low)} question(s)")
    print(f"{'='*50}\n")

    md = format_markdown(results)
    out_path = Path(__file__).parent / "results.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"Results saved to {out_path}")
