# Implementation Checklist & Compliance Matrix

**Project Title:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Status Date:** November 2026  

---

## 1. Compliance Matrix

| Phase | Requirement | Primary File(s) | Status | Evidence / Verification Target |
|---|---|---|---|---|
| **Phase 1** | Project directory structure | Root directory | Completed | Directory tree verified |
| **Phase 1** | Environment & requirements config | `requirements.txt`, `.env.example`, `.gitignore` | Completed | Config files created |
| **Phase 1** | README & Documentation foundation | `README.md`, `docs/implementation_checklist.md` | Completed | Documentation initiated |
| **Phase 2** | Dataset identification & verification | `scripts/prepare_dataset.py`, `src/dataset_loader.py` | Completed | 9,533 raw ingested; Zenodo (134 records, 403 gate) + OBDex (CC0) documented in `data/source_inventory.csv` |
| **Phase 2** | Preprocessing, validation & deduplication | `src/preprocessing.py`, `src/dataset_validator.py` | Completed | 9,532 valid unique records; >= 5,000 threshold exceeded (190.6%); 10/10 pytest passed |
| **Phase 3** | Document & query embeddings generation | `src/embeddings.py` | Completed | `all-MiniLM-L6-v2` 384-dim; batch encoding; unit norm verified |
| **Phase 3** | ChromaDB persistence & collection init | `src/chroma_manager.py`, `scripts/build_database.py` | Completed | 9,532 records persisted in `database/chroma_db` (180MB SQLite + HNSW) |
| **Phase 3** | Full CRUD implementation & verification | `src/crud_operations.py`, `tests/test_chroma.py` | Completed | Create, Read, Update, Delete verified on isolated test fixture; 18/18 pytest passed |
| **Phase 4** | Semantic search & Top-K retrieval | `src/semantic_search.py`, `scripts/run_queries.py` | Completed | All 10 queries executed for K=5 and K=10; ranked by distance ascending; zero duplicates |
| **Phase 4** | Metadata filtering (single & compound) | `src/metadata_filters.py` | Completed | 5 multi-condition compound `$and` filters executed & verified across subsystems |
| **Phase 4** | 10 Documented troubleshooting queries | `data/queries/assignment_queries.json` | Completed | 10 realistic diagnostic symptom queries covering all 4 automotive subsystems; 29/29 pytest passed |
| **Phase 5** | NumPy exhaustive similarity engine | `src/similarity_metrics.py` | Completed | Euclidean (L2), Cosine, Dot product; zero-division safety; tie-breaking |
| **Phase 5** | Metric comparison experiments | `scripts/run_similarity_comparison.py` | Completed | All 10 queries x 3 metrics x 2 K-values (60 evaluations); Phase 4/5 reconciliation verified (`experiments/phase4_phase5_reconciliation.md`); 39/39 pytest passed |
| **Phase 6** | LLM provider integration | `src/llm_provider.py` | Completed | Local Ollama, OpenAI-compatible API, and Mock provider for offline CI |
| **Phase 6** | RAG pipeline with grounded citations | `src/rag_pipeline.py`, `scripts/run_rag.py` | Completed | Top-K context formatting, grounded prompt with anti-hallucination rules & [VTR-XXXXX] citations |
| **Phase 6** | Context vs No-Context comparison | `src/rag_evaluation.py`, `experiments/` | Completed | All 10 queries evaluated side-by-side; citation fidelity, safety & specificity metrics; 51/51 pytest passed |
| **Phase 7** | Streamlit multi-page application | `app.py`, UI views | Pending | 7 distinct interactive tabs/pages |
| **Phase 8** | Academic report & viva documentation | `docs/report_draft.md`, `docs/viva_questions.md` | Pending | Academic standard report & Q&A |
| **Phase 8** | Final end-to-end automated validation | `scripts/validate_project.py` | Pending | Zero-tolerance validation script |

---

## 2. Requirement Verification Criteria

1. **Dataset Authenticity & Volume:**
   - [x] No fake or synthetically duplicated records to hit 5,000.
   - [x] All records tagged with authentic origin and license.
   - [x] Verified unique count $\ge 5,000$ (Achieved: 9,532 records).

2. **ChromaDB Functionality:**
   - [x] Local persistence reload test passes.
   - [x] CRUD tested on sandbox records without corrupting production data.
   - [x] Collection inspection accurately reports document counts (9,532 records).

3. **NumPy vs ChromaDB Mathematics:**
   - [x] Normalized vs unnormalized vector behavior explicitly documented.
   - [x] Distance (smaller is better) vs Similarity (larger is better) strictly handled.
   - [x] Exhaustive computation across all $N$ records (9,532 records evaluated per query).
   - [x] Exact kNN vs Approximate kNN (HNSW graph recall vs linear scan) analyzed.

4. **RAG Reliability & Safety:**
   - [x] Explicit hallucination mitigation prompt instructions.
   - [x] Fallback when context is insufficient.
   - [x] Mandatory automotive safety disclaimer included.
   - [x] Mandatory source citations [VTR-XXXXX] extracted and validated.
   - [x] Context vs. No-Context baseline comparison evaluated across all 10 queries.

