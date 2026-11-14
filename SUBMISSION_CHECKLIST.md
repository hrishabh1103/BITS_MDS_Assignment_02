# BITS MDS Assignment 2 — Submission Checklist

**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Group:** Group 20  
**Repository:** `https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git`  
**Latest Verified Commit:** Current `origin/main` commit  
**Submission Package:** `Group-20_Project_Source_Code_Final.zip`, `reports/Group-20.pdf`, `reports/Group-20.docx`  

---

## 1. Team Identification & Compliance
- [x] **Official Group Number:** Group 20
- [x] **All 5 Team Members Documented:**
  - Priya N (`2026NS12087`) — 20% Contribution
  - Mohamed Ibrahim M (`2026NS12021`) — 20% Contribution
  - Hrishabh Gupta (`2026NS12122`) — 20% Contribution
  - Aditya Singhal (`2026NS12028`) — 20% Contribution
  - Rupesh Kumar Singh (`2026NS12128`) — 20% Contribution
- [x] **Equal Contribution Consensus:** Unanimous 20.0% contribution confirmed and documented across all documents (Total: 100.0%).
- [x] **Cover Page Consistency:** `reports/Group-20.pdf` and `reports/Group-20.docx` reflect identical group and member information.

---

## 2. Core Assignment Deliverables Checklist

### 2.1 Dataset Requirements ($\ge 5,000$ authentic records)
- [x] **Authentic Dataset:** 9,532 automotive diagnostic trouble records based on SAE J2012 / ISO 15031-6 standard (DTC definitions, symptoms, and causes).
- [x] **Zero Synthetic Fabrication:** No synthetic text generation, no duplicate records (0 duplicate IDs).
- [x] **Zenodo 15626055 Evaluation:** Documented in `docs/DATASET_DOCUMENTATION.md` and `data/source_inventory.csv` (134 records, HTTP 403, supplemented by OBDex open standard).
- [x] **Standardized Schema:** Complete 16-field JSON schema in `data/processed/vehicle_troubleshooting.json`.
- [x] **Validation Suite:** Automated validation via `src/dataset_validator.py` and `tests/test_dataset.py`.

### 2.2 ChromaDB Vector Database Implementation
- [x] **Persistent Database:** ChromaDB PersistentClient stored in `database/chroma_db/` (`chroma.sqlite3` + HNSW index).
- [x] **Verified Collection:** `vehicle_troubleshooting_kb` containing exactly 9,532 records (reproducible via `python scripts/build_database.py`).
- [x] **Embedding Dimensions:** 384 dense float32 dimensions (`all-MiniLM-L6-v2`), unit-normalized.
- [x] **Distance Space:** Cosine distance space (`{"hnsw:space": "cosine"}`).
- [x] **CRUD Operations:** Tested in sandbox isolation using `TEST-VTR-CRUD-001` without altering the 9,532 records.
- [x] **Multi-Session Persistence:** Verified across distinct process invocations (`del client_1`, spawn `client_2`).

### 2.3 Vector Similarity & Mathematical Benchmarking
- [x] **Pure Vectorized NumPy:** Implemented Euclidean Distance ($L_2$), Cosine Similarity, and Dot Product in `src/similarity_metrics.py`.
- [x] **Exhaustive Evaluation:** 60 evaluations ($10\text{ queries} \times 3\text{ metrics} \times 2\text{ values of }K$) executed via `scripts/run_similarity_comparison.py`.
- [x] **Mathematical Rank Proof:** Verified rank equivalence on unit sphere ($\rho = 1.0000$).
- [x] **Synthetic Divergence Study:** Controlled unnormalized experiment showing metric divergence when vector norms vary.
- [x] **ChromaDB HNSW vs NumPy:** Benchmark comparison documented in `docs/RETRIEVAL_METHODOLOGY.md`.

### 2.4 Retrieval-Augmented Generation (RAG) Subsystem
- [x] **Grounded Pipeline:** `src/rag_pipeline.py` with system prompt v2.2.0.
- [x] **Anti-Hallucination Guardrails:** Zero specification hallucination, causality vs correlation rules, mandatory `[VTR-XXXXX]` citations.
- [x] **Provider Abstraction:** `src/llm_provider.py` supporting Ollama, OpenAI-compatible APIs, and Mock mode.
- [x] **Real LLM Inference:** Meta Llama 3.2 (3.2B parameters) running locally via Ollama with Metal acceleration.
- [x] **Comparative Evaluation:** Side-by-side RAG vs No-Context baseline evaluation across all 10 queries (Q01–Q10) via `scripts/run_rag.py`.
- [x] **Negative Findings:** Documented boundary cases (Q03 parasitic drain, Q09 airbag squib testing).

### 2.5 Streamlit Interactive Dashboard
- [x] **Multi-Page Application:** 5 distinct views routed via `app.py` and `src/ui/`:
  - 🏠 Home / Dashboard (`src/ui/home_page.py`)
  - 🔧 Troubleshooting Assistant (`src/ui/assistant_page.py`)
  - 🔍 Semantic Search (`src/ui/search_page.py`)
  - 📊 Evaluation Dashboard (`src/ui/evaluation_page.py`)
  - 📖 About / Dataset (`src/ui/about_page.py`)
- [x] **Live Query Execution:** Real-time semantic search and RAG generation with live/mock toggle.
- [x] **Safety Warning Banners:** Programmatic guardrail warnings for SRS, high-voltage, brakes, and cooling.
- [x] **Visual Styling:** Polished automotive dark-mode theme with metrics cards and status indicators.

### 2.6 Academic Reports & Documentation
- [x] **PDF Report:** `reports/Group-20.pdf` (16-page official comprehensive academic report with tables, math derivations, and diagrams).
- [x] **DOCX Report:** `reports/Group-20.docx` (100% substantive equivalence with PDF).
- [x] **Requirement Traceability:** `reports/requirement_evidence_matrix.md`.
- [x] **Architecture Visuals:** `reports/figures/system_architecture.png` and `reports/figures/streamlit_home_page.png`.
- [x] **Comprehensive Docs:** 9 dedicated markdown documents in `docs/`.
- [x] **Standardized Queries:** `queries/assignment_queries.json` and `queries/README.md`.

### 2.7 Automated Test Suite
- [x] **Total Automated Tests:** 75 tests across 7 test files in `tests/`.
- [x] **Pass Rate:** 100% (75 passed, 0 failed in ~16s).
