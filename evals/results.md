# Retrieval Eval Results

**Date:** 2026-06-11  
**Collection:** `govt_schemes`  
**Embedding model:** `BAAI/bge-small-en-v1.5`  
**Eval set:** 20 questions, hit = answer phrase found in top-5 chunks  
**Low-score threshold:** 0.65

## Summary

| Metric | Value |
|--------|-------|
| Hit rate | **14/20 (70%)** |
| Avg top-1 score | **0.772** |
| Avg top-5 mean score | **0.748** |
| Questions below 0.65 | **0** |

## Per-question Results

| # | Topic | Hit | Top-1 Score | Avg Top-5 | Top Source | Flag |
|---|-------|-----|-------------|-----------|------------|------|
| 1 | Total Expenditure | ✅ | 0.807 | 0.800 | bag6.pdf p1 |  |
| 2 | Capital Expenditure | ❌ | 0.739 | 0.737 | allsbe.pdf p73 |  |
| 3 | Budget Documents | ✅ | 0.782 | 0.726 | Key_to_Budget_Document_2026.pdf p2 |  |
| 4 | Finance Minister | ✅ | 0.768 | 0.708 | Finance_Bill.pdf p9 |  |
| 5 | Finance Bill | ✅ | 0.871 | 0.794 | Finance_Bill.pdf p9 |  |
| 6 | Interest Payments | ✅ | 0.766 | 0.760 | allsbe.pdf p148 |  |
| 7 | Housing & Urban Affairs | ✅ | 0.786 | 0.778 | allsbe.pdf p211 |  |
| 8 | Jal Shakti | ❌ | 0.765 | 0.762 | allsbe.pdf p183 |  |
| 9 | Centrally Sponsored Schemes | ❌ | 0.765 | 0.754 | allsbe.pdf p324 |  |
| 10 | Roads & Bridges | ✅ | 0.778 | 0.761 | allsbe.pdf p294 |  |
| 11 | Annual Financial Statement | ❌ | 0.653 | 0.648 | Finance_Bill.pdf p102 |  |
| 12 | Finance Commission Grants | ❌ | 0.774 | 0.757 | allsbe.pdf p156 |  |
| 13 | Output Outcome Framework | ✅ | 0.793 | 0.729 | OutcomeBudgetE2026_2027.pdf p5 |  |
| 14 | FRBM Act | ✅ | 0.746 | 0.698 | Key_to_Budget_Document_2026.pdf p6 |  |
| 15 | Finance Bill Purpose | ✅ | 0.774 | 0.728 | Finance_Bill.pdf p171 |  |
| 16 | Central Sector Schemes | ❌ | 0.771 | 0.761 | allsbe.pdf p324 |  |
| 17 | Renewable Energy | ✅ | 0.781 | 0.774 | allsbe.pdf p256 |  |
| 18 | Labour & Employment | ✅ | 0.798 | 0.776 | allsbe.pdf p232 |  |
| 19 | Expenditure Profile | ✅ | 0.765 | 0.746 | Key_to_Budget_Document_2026.pdf p7 |  |
| 20 | MSME | ✅ | 0.767 | 0.759 | allsbe.pdf p242 |  |

## Notes

- Hit detection uses case-insensitive substring match of a key answer phrase in retrieved chunks.
- Scores are cosine similarities from `BAAI/bge-small-en-v1.5` (BGE, normalised).
- A score ≥ 0.65 indicates strong semantic overlap; ≥ 0.70 is high confidence.