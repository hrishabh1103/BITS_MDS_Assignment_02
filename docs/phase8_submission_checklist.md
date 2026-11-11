# Phase 8 Submission Readiness & Integrity Checklist

**Course:** BITS Pilani WILP — Modern Database Systems (Assignment 2)  
**Project Title:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Date of Audit:** November 2026  
**Repository Branch:** `main`  
**Verified Commit Hash:** `0c889c1`  
**Remote Git URL:** `https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git`  

---

## 1. Submission Package Checklist

| Category | Component / Artifact | Path | Status | Verification Detail |
|:---|:---|:---|:---:|:---|
| **Reports** | Academic Report (PDF) | `reports/Group-[number].pdf` | Ready | Professional PDF format, 20 sections, diagrams & tables included. |
| **Reports** | Academic Report (DOCX) | `reports/Group-[number].docx` | Ready | Editable Microsoft Word format with styles, tables, and images. |
| **Reports** | Requirement Matrix | `reports/requirement_evidence_matrix.md` | Ready | Traceability matrix for all 13 core assignment requirements. |
| **Reports** | Architecture Diagram | `reports/figures/system_architecture.png` | Ready | High-res (300 DPI) end-to-end architecture flowchart. |
| **Reports** | Genuine UI Screenshot | `reports/figures/streamlit_home_page.png` | Ready | 1440x1080 genuine screenshot from headless Chrome. |
| **Codebase** | Python Package Source | `src/` (11 modules) | Ready | Pure Python, modular architecture, fully typed. |
| **Application**| Streamlit Entrypoint | `app.py` & `src/ui/` (6 modules) | Ready | Multi-page Streamlit application verified via AppTest. |
| **Database** | Persistent ChromaDB Store | `database/chroma_db/chroma.sqlite3` | Ready | Verified persistent SQLite (~180MB) holding 9,532 records. |
| **Dataset** | Processed Dataset JSON | `data/processed/vehicle_troubleshooting.json` | Ready | 9,532 records, 13.9 MB, valid schema, CC0 1.0 license. |
| **Dataset** | Source Attribution CSV | `data/source_inventory.csv` | Ready | Full attribution for Zenodo (15626055) and OBDex. |
| **Experiments**| Phase 4 Semantic Search | `experiments/semantic_search_results.json` | Ready | 10 queries, Top-5 and Top-10 rankings. |
| **Experiments**| Phase 4 Metadata Filter | `experiments/metadata_filter_results.json` | Ready | 5 compound `$and` filter evaluations. |
| **Experiments**| Phase 5 NumPy Comparison | `experiments/similarity_comparison_results.json`| Ready | 60 evaluations across Euclidean, Cosine, Dot product. |
| **Experiments**| Phase 5 Reconciliation | `experiments/phase4_phase5_reconciliation.md` | Ready | Phase 4/5 Top-1 ranking identity mathematically proven. |
| **Experiments**| Phase 6.1 Real RAG Eval | `experiments/rag_real_results.json` | Ready | 10 queries executed on live Ollama Llama 3.2. |
| **Experiments**| Phase 6.1 Comparison | `experiments/rag_real_context_vs_baseline.json`| Ready | RAG vs zero-context baseline comparison. |
| **Experiments**| Phase 6.1 Summary CSV | `experiments/rag_real_evaluation.csv` | Ready | 100% citation precision, 96% citation recall. |
| **Test Suite** | Pytest Automation | `tests/` (7 test modules) | Ready | **75 passed, 0 failed** (100% pass rate in 14.33s). |
| **Environment**| Requirements Spec | `requirements.txt` | Ready | Pinned dependencies including `python-docx` and `reportlab`. |
| **Environment**| Environment Template | `.env.example` | Ready | Sample config; `.env` strictly gitignored. |

---

## 2. Integrity & Quality Gates

### 2.1 Database Preservation Gate
- [x] Production collection `vehicle_troubleshooting_kb` has not been corrupted or rebuilt.
- [x] Collection count strictly verified at **9,532 records**.
- [x] Document embeddings verified at **384 float32 dimensions** with unit normalization.

### 2.2 Academic Honesty Gate
- [x] Dataset is accurately characterized as **9,532 curated Diagnostic Trouble Code (DTC) entries**, not 9,532 real repair cases.
- [x] Citation precision and recall are explicitly defined as *citation provenance consistency*, not factual correctness.
- [x] Negative findings (Q03 high-voltage retrieval mismatch on 12V battery drain and Q09 initial airbag squib instruction risk) are openly disclosed with full explanation of safety guardrail resolutions.
- [x] No query results, rankings, or evaluation metrics have been fabricated or hand-edited.

### 2.3 Automotive Safety Gate
- [x] **Airbag Safety**: Ohmmeter, multimeter, and test-light probing across squib circuits strictly prohibited. Battery disconnection explicitly qualified as insufficient by itself to ensure safety.
- [x] **High-Voltage EV**: Shock hazard warnings (300V–800V) mandate certified technician lockout/tagout. Slogans that Class-0 gloves alone make work safe are completely eliminated.
- [x] **Hydraulic Brakes**: Sinking brake pedal produces an unequivocal **DO NOT DRIVE** warning and mandatory towing instruction.
- [x] **Cooling Systems**: Unsafe upper radiator hose squeezing instructions removed; conservative manufacturer-procedure directives enforced.
- [x] **Domain Mismatch**: Standard 12V battery drain queries flagged against using retrieved high-voltage EV charger records.

### 2.4 Code & Configuration Gate
- [x] Zero secrets or API keys staged or committed. `.env` is protected by `.gitignore`.
- [x] Clean Git working tree on `main` branch.
- [x] Remote GitHub repository synchronized at commit [`0c889c1`](https://github.com/hrishabh1103/BITS_MDS_Assignment_02/commit/0c889c1).

---

## 3. Items Requiring Student / Group Confirmation Before Final Upload

Before submitting the report through the BITS Pilani LMS portal, students must perform the following manual updates:
1. **Group Number Replacement**:
   - Replace placeholder `[number]` in `reports/Group-[number].pdf` and `reports/Group-[number].docx` with your official BITS Pilani assigned Group Number (e.g. `Group-12.pdf`).
2. **Student Member Names & BITS IDs**:
   - Fill in actual Student Names, BITS Pilani Student IDs, and Course Section details on the Cover Page (Section 1) and Team Contribution Table (Section 19).
3. **Repository URL**:
   - Confirm your GitHub submission URL is accessible by evaluators: `https://github.com/hrishabh1103/BITS_MDS_Assignment_02`.
