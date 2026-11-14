# Project Overview — Vehicle Troubleshooting Assistant

**Course:** Modern Database Systems (Assignment 2)  
**Academic Institution:** BITS Pilani Work Integrated Learning Programmes (WILP)  
**Group:** 20  
**Repository:** `BITS_MDS_Assignment_02`  

---

## 1. Project Background and Motivation

Diagnosing modern motor vehicles requires navigating thousands of standardized Diagnostic Trouble Codes (DTCs) across engine, transmission, braking, electrical, and network communication subsystems. When diagnosing an issue in an automotive workshop or during road service, two practical challenges routinely arise:

1. **Limitations of Keyword and Exact-Code Lookup:** Factory repair manuals and diagnostic portals are indexed primarily by exact DTC numbers (such as `P00B7` or `C0291`). When a customer reports a natural-language symptom (e.g., *"brake pedal slowly sinks to the floorboard at red lights"*), or when multiple symptoms occur together without an explicit trouble code, keyword search frequently fails to surface the relevant technical service bulletin or test sequence.
2. **Risks of Ungrounded Generative AI:** General-purpose Large Language Models (LLMs) can produce fluent answers, but in automotive technical domains they present significant hallucination risks. An ungrounded model may invent component replacement sequences, fabricate torque specifications, suggest dangerous multimeter resistance measurements across pyrotechnic airbag squibs, or confuse internal combustion 12V battery drain with high-voltage electric vehicle charging systems.

To address these challenges, our group built the **Vehicle Troubleshooting Assistant**, a domain-grounded retrieval-augmented generation (RAG) system supported by an embedded, persistent vector database (**ChromaDB**) indexing 9,532 authentic automotive diagnostic records.

---

## 2. Project Objectives

The project was executed to satisfy the core objectives of WILP Modern Database Systems Assignment 2:

- **Curate and Validate a Real Knowledge Base:** Compile over 5,000 non-synthetic, standardized vehicle diagnostic records with verified symptoms, probable causes, diagnostic procedures, and safety warnings. (The resulting dataset contains 9,532 records, exceeding the threshold by +90.6%).
- **Implement a Persistent Vector Database:** Store and index dense vector embeddings in ChromaDB using a persistent SQLite backend and HNSW graph indexing in cosine distance space.
- **Formulate Domain-Specific Benchmark Queries:** Define 10 diagnostic queries spanning multiple vehicle subsystems to serve as an evaluation suite for retrieval and generation.
- **Conduct Exhaustive Mathematical Similarity Comparison:** Implement pure NumPy vector distance routines (Euclidean distance, Cosine similarity, and Dot product) to benchmark against ChromaDB and prove ranking equivalence under vector unit normalization.
- **Build a Grounded RAG Pipeline:** Connect semantic vector retrieval to a language model using strict prompt constraints, requiring in-text citations (`[VTR-XXXXX]`) to establish reference provenance.
- **Implement Multi-Tier Automotive Safety Guardrails:** Programmatically detect and intervene when queries or retrieved context involve hazardous domains (SRS airbags, 300V–800V EV loops, hydraulic brake failures, thermal cooling scalds, and ICE vs. EV context mismatches).
- **Deliver an Interactive Web Dashboard:** Provide an intuitive Streamlit dashboard allowing users to query the system, filter by metadata, inspect benchmark evaluation data, and examine dataset distributions.
- **Verify Through Automated Testing:** Ensure software reliability and database persistence through a comprehensive test suite (75 passing tests).

---

## 3. Technology Stack

We chose a modular, lightweight Python stack that runs locally without requiring costly cloud infrastructure:

- **Language:** Python 3.11
- **Vector Database:** ChromaDB 0.5+ (embedded mode with SQLite metadata storage and binary HNSW graphs)
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors, $L_2$ normalized)
- **Numerical Computing:** NumPy 1.26+ (vectorized matrix computations for linear-scan comparisons)
- **LLM Integration:** Ollama (local inference with Meta Llama 3.2 3B) alongside a deterministic `MockLLMProvider` for offline automated grading
- **User Interface:** Streamlit 1.35+ with interactive Plotly 5.20+ charts
- **Testing:** Pytest 8.0+ and Pytest-Cov
- **Reporting:** ReportLab and python-docx for automated academic report generation

---

## 4. Key Engineering Highlights

### 4.1 Persistent Storage Without Synthetic Padding
The dataset contains 9,532 unique diagnostic records normalized into a strict schema. Standardized DTC definitions, probable causes, and symptom descriptions were sourced from public-domain automotive repositories (Zenodo Record 15626055 and OBDex under CC0 1.0). Diagnostic procedures were normalized for academic exploration. Zero synthetic records were created to reach volume targets.

### 4.2 Mathematical Equivalence Proof
Using pure NumPy, we computed 60 evaluations across 10 queries, 3 distance metrics, and 2 retrieval cardinalities ($K=5, 10$). Because embeddings are $L_2$-normalized to unit length ($\|\mathbf{u}\|_2 = 1$), the squared Euclidean distance simplifies to:

$$\|\mathbf{u} - \mathbf{v}\|_2^2 = 2 - 2(\mathbf{u} \cdot \mathbf{v}) = 2(1 - \cos\theta)$$

This proves that minimizing Euclidean distance is strictly monotonic with maximizing Cosine similarity and Dot product, explaining why all three metrics produce identical nearest-neighbor rankings.

### 4.3 Provenance Consistency vs. Ground Truth
In Phase 6.1 real LLM evaluation using Meta Llama 3.2 (3B), our grounded RAG pipeline achieved **100.0% Citation Precision** (48/48 citations valid) and **96.0% Citation Recall** (48/50 retrieved records cited), compared to 0 citations in unassisted baseline generation. We explicitly document that this metric measures *reference provenance consistency* (the model cites actual retrieved records without inventing record IDs), not absolute mechanical correctness.

### 4.4 Defense-in-Depth Safety Guardrails
Our evaluation revealed critical negative findings when using raw LLM outputs (e.g., advising an ohmmeter resistance check across an airbag squib, or suggesting EV high-voltage cable inspection for an ordinary 12V alternator drain). We designed backend safety interceptors in `src/safety_guardrails.py` that detect these conditions and inject mandatory safety warnings and technician protocols before the diagnostic advice reaches the user.

