# Step-by-Step Run & Evaluation Instructions

**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Group:** 20  
**Repository:** `https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git`  

---

## 1. Prerequisites & System Requirements

- **Operating System:** macOS (Apple Silicon or Intel), Linux (Ubuntu/Debian), or Windows (WSL2 recommended).
- **Python Version:** Python 3.10 or 3.11 (`python3 --version`).
- **Disk Space:** ~2.5 GB (including virtual environment, dependencies, and vector database).
- **RAM:** Minimum 8 GB (16 GB recommended for running local LLM).
- **Optional Local LLM Runtime:** [Ollama](https://ollama.com/) with `llama3.2` model (`ollama run llama3.2`). *Note: If Ollama is not installed or running, the entire test suite and Streamlit application operate seamlessly using the built-in deterministic Mock provider.*

---

## 2. Environment Setup

### 2.1 Clone Repository
```bash
git clone https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git
cd BITS_MDS_Assignment_02
```

### 2.2 Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or: .venv\Scripts\activate   # On Windows
```

### 2.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Database Initialization & Verification

The repository includes pre-built persistence files under `database/chroma_db/`. You can immediately verify or rebuild the database.

### 3.1 Verify Existing Database Count
```bash
python3 -c "from src.chroma_manager import ChromaDBManager; mgr = ChromaDBManager(); print('Total Records:', mgr.get_count())"
# Expected output: Total Records: 9532
```

### 3.2 Optional: Rebuild Database from Source Dataset
If you wish to rebuild the vector database from raw JSON records:
```bash
python scripts/build_database.py
```
This script reads `data/processed/vehicle_troubleshooting.json`, generates 384-dimensional embeddings via Sentence Transformers, and inserts all 9,532 records into ChromaDB in batches of 500 records (~2 minutes on CPU).

---

## 4. Automated Testing & Verification

Run the full automated test suite containing 75 test cases:

```bash
pytest tests/ -v
```

Expected output:
```text
============================== 75 passed in ~14s ==============================
```

Test coverage includes:
- `tests/test_dataset.py`: Schema validation, 0 duplicate IDs, 16 mandatory fields.
- `tests/test_chroma.py`: ChromaDB initialization, persistence reload, count verification.
- `tests/test_crud.py`: Isolated CRUD lifecycle (`TEST-VTR-CRUD-001`).
- `tests/test_embeddings.py`: SentenceTransformer output shape (384) and unit normalization.
- `tests/test_similarity.py`: Pure NumPy Cosine, Euclidean, and Dot Product calculations.
- `tests/test_rag.py`: Grounded prompt assembly, citation parsing, Mock provider generation.
- `tests/test_safety.py`: Domain safety guardrails (SRS, EV, brakes, cooling, drain).
- `tests/test_ui.py`: Streamlit multi-page component rendering and error states.

---

## 5. Launching the Interactive Streamlit Dashboard

Launch the 5-page interactive troubleshooting assistant:

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`.

### Navigating the Multi-Page Application:
1. **Page 1: Home / Dashboard:** Overview of project metrics, collection count (9,532), and system architecture summary.
2. **Page 2: Troubleshooting Assistant:** Interactive diagnostic assistant. Enter any symptom (e.g., *"car hesitates during acceleration with check engine light"*) or select from predefined assignment queries (Q01–Q10). Toggle between Real Ollama LLM and Mock provider.
3. **Page 3: Semantic Search Explorer:** Direct search across the 9,532 records with subsystem and severity filters, displaying similarity scores and raw metadata.
4. **Page 4: Mathematical Similarity Benchmarking:** Interactive vector comparison showing Cosine, Euclidean, and Dot Product calculations side-by-side.
5. **Page 5: System Architecture & Docs:** In-app documentation and component architecture diagrams.

---

## 6. Running Headless Experimentation Scripts

All research experiments can be executed independently from the command line:

### 6.1 Semantic Search Evaluation (Phase 4)
```bash
python scripts/run_semantic_search.py
# Generates top-K retrieval results in experiments/
```

### 6.2 Mathematical Similarity Comparison (Phase 5)
```bash
python scripts/run_similarity_comparison.py
# Computes 60 evaluations across Cosine, L2, and Dot Product using pure NumPy
```

### 6.3 RAG vs Baseline Comparative Evaluation (Phase 6)
```bash
# Offline Mock Mode (instant, no GPU/LLM required):
python scripts/run_rag.py --mode mock

# Real LLM Mode (requires Ollama running with llama3.2):
python scripts/run_rag.py --mode real
```

### 6.4 Academic Report Regeneration (Phase 8)
```bash
python scripts/generate_final_report.py
# Regenerates reports/Group-20.pdf and reports/Group-20.docx with 100% equivalence
```

