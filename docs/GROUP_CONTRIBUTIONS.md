# Team Contributions & Collaborative Lifecycle Statement

**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Group:** 20  

---

## 1. Confirmed Group Membership & Contribution Ratios

Following full group discussion and unanimous consensus across all team members, the contribution percentage is agreed to be **strictly equal (20.0% each)** across all five students. The project was executed through continuous pair-programming, joint architecture reviews, collaborative verification sessions, and shared academic documentation drafting.

| Member Name | BITS Student ID | Confirmed Contribution | Primary Collaborative Focus |
|---|---|---|---|
| **Priya N** | `2026NS12087` | **20.0%** | Dataset provenance, schema design, and validation |
| **Mohamed Ibrahim M** | `2026NS12021` | **20.0%** | ChromaDB persistence, HNSW indexing, and CRUD verification |
| **Hrishabh Gupta** | `2026NS12122` | **20.0%** | Vector similarity math, NumPy benchmarks, and embedding engine |
| **Aditya Singhal** | `2026NS12028` | **20.0%** | RAG pipeline, prompt engineering, and LLM abstraction layer |
| **Rupesh Kumar Singh** | `2026NS12128` | **20.0%** | Safety guardrails, Streamlit UI dashboard, and testing |

---

## 2. Collaborative Project Lifecycle Overview

Rather than dividing the system into isolated, siloed modules, the group adopted an integrated engineering lifecycle where all team members participated across every milestone:

### Phase 1: Problem Definition & Architecture Conception
- Joint formulation of the hybrid vector-relational diagnostic assistant concept.
- Selection of the SAE J2012 / ISO 15031-6 standard dataset after evaluating and documenting the limitations of Zenodo record 15626055.
- Architecture blueprinting for the 5-layer system (Data, Vector Store, Retrieval, Generation, Presentation).

### Phase 2: Ingestion & ChromaDB Persistent Storage
- Collaborative development of `src/preprocessing.py` and `src/chroma_manager.py`.
- Validation of 9,532 authentic diagnostic records with zero ID collisions and complete 16-field schemas.
- Implementation of the CRUD sandbox test harness (`TEST-VTR-CRUD-001`) and multi-session persistence verification.

### Phase 3 & 4: Embeddings & Semantic Retrieval Engine
- Deployment and testing of `sentence-transformers/all-MiniLM-L6-v2` with explicit $L_2$ unit normalization.
- Evaluation of Top-K retrieval ($K=3, 5, 10$) across 10 diverse automotive symptom queries (Q01–Q10).
- Analysis of semantic matching accuracy between colloquial symptom complaints and formal DTC codes.

### Phase 5: Exhaustive Mathematical Similarity Benchmarking
- Pure vectorized NumPy implementation of Cosine Similarity, Euclidean Distance ($L_2$), and Dot Product.
- Execution and analysis of 60 experimental configurations ($10\text{ queries} \times 3\text{ metrics} \times 2\text{ values of }K$).
- Derivation and empirical validation of mathematical rank equivalence on unit-normalized hyperspheres ($\rho = 1.0000$).
- Controlled synthetic experimentation proving rank divergence on unnormalized vector spaces.

### Phase 6 & 6.1: RAG Pipeline & Real LLM Validation
- Grounded prompt engineering (`SYSTEM_PROMPT` v2.2.0) with strict square-bracket citation rules (`[VTR-XXXXX]`).
- Provider abstraction layer supporting local Ollama (Llama 3.2 3B), OpenAI-compatible APIs, and deterministic Mock CI execution.
- Side-by-side comparative evaluation of RAG versus ungrounded parametric baseline responses across all 10 assignment queries.

### Phase 7 & 7.2: Streamlit Multi-Page Assistant & Safety Guardrails
- Development of the 5-page interactive dashboard (Home, Troubleshooting, Semantic Search, Mathematical Benchmark, System Architecture).
- Implementation of domain safety guardrails: SRS squib probing prohibition, 300V–800V EV warnings, spongy brake DO NOT DRIVE warning, cooling scald prevention, and ICE vs EV drain isolation.
- Comprehensive regression testing: 75 automated pytest test cases passing with 100% success.

### Phase 8: Academic Reporting & Submission Packaging
- Joint drafting of the final academic report (`reports/Group-20.pdf` and `reports/Group-20.docx`).
- Requirement-to-evidence traceability mapping across all assignment deliverables.
- Final code audit, documentation cleanup, and preparation of the submission archive.

