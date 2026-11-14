# Step-by-Step Run & Evaluation Instructions

**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Group:** Group 20  
**Repository:** `https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git`  

---

## 1. Prerequisites & System Requirements

- **Operating System:** macOS (Apple Silicon or Intel), Linux (Ubuntu/Debian), or Windows (WSL2 recommended).
- **Python Version:** Python 3.10 or 3.11 (`python3 --version`).
- **Disk Space:** ~2.5 GB (including virtual environment, dependencies, and vector database).
- **RAM:** Minimum 8 GB (16 GB recommended for running local LLM).
- **Optional Local LLM Runtime:** [Ollama](https://ollama.com/) with `llama3.2` model (`ollama run llama3.2`). *Note: If Ollama is not installed or running, the entire test suite, headless evaluation, and Streamlit application operate seamlessly using the built-in deterministic Mock provider.*

---

## 2. Environment Setup

### 2.1 Clone Repository or Extract Submission ZIP
```bash
# If cloning from GitHub:
git clone https://github.com/hrishabh1103/BITS_MDS_Assignment_02.git
cd BITS_MDS_Assignment_02

# Or if evaluating from the submission ZIP:
unzip Group-20_Project_Source_Code_Final.zip -d BITS_MDS_Assignment_02
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

The submission ZIP archive excludes the ~195 MB binary ChromaDB database to remain lightweight (< 10 MB). The persistent collection can be immediately built from the included `data/processed/vehicle_troubleshooting.json` file.

### 3.1 Build the ChromaDB Persistent Database
```bash
python scripts/build_database.py
```
*What this does:* Reads `data/processed/vehicle_troubleshooting.json` (9,532 records), computes 384-dimensional dense vectors using `all-MiniLM-L6-v2` with $L_2$ normalization in batches of 64, and inserts all records into the persistent collection `vehicle_troubleshooting_kb` under `database/chroma_db/` in chunks of 500 records (~2 minutes on CPU).

### 3.2 Verify Database Record Count
```bash
python3 -c "from src.chroma_manager import ChromaDBManager; mgr = ChromaDBManager(); print('Total Records:', mgr.get_count())"
# Expected output: Total Records: 9532
```

---

## 4. Automated Testing & Verification

Run the full automated test suite containing exactly 75 test cases across 7 test modules:

```bash
pytest tests/ -v
```

Expected verified output:
```text
======================= 75 passed, 10 warnings in ~16s =======================
```

The 7 verified test files in `tests/`:
1. `tests/test_chroma.py` (8 tests): Embedding dimensions (384), $L_2$ unit normalization, collection count (9,532), record retrieval, multi-session reload persistence, isolated CRUD (`TEST-VTR-CRUD-001`), and semantic query execution.
2. `tests/test_dataset.py` (10 tests): File existence, $\ge 5,000$ volume threshold (9,532 verified), zero duplicate IDs, 16 mandatory schema fields, non-empty diagnostic steps, and category validation.
3. `tests/test_numpy_similarity.py` (11 tests): Hand-calculated Euclidean ($L_2$), Cosine similarity, and Dot product, zero-vector stability, exact rank preservation on normalized vectors, synthetic unnormalized divergence, and 60-configuration runner.
4. `tests/test_phase7_dashboard.py` (8 tests): Streamlit compilation, UI components, data caching, preset queries loader, and dataset summary loaders.
5. `tests/test_rag.py` (11 tests): Mock provider deterministic behavior, provider factory, grounded context formatting, prompt construction, citation extraction (`[VTR-XXXXX]`), and citation fidelity scoring.
6. `tests/test_safety_guardrails.py` (16 tests): Airbag squib ohmmeter prohibition, EV high-voltage lockouts, spongy brake DO NOT DRIVE warning, cooling scald prevention (no hose-squeezing), and 12V ICE vs EV drain isolation.
7. `tests/test_search.py` (11 tests): Top-5 and Top-10 cardinality, distance ordering ascending, ID integrity, and compound metadata filters (`$and`).

---

## 5. Launching the Interactive Streamlit Web Application

Launch the multi-page Streamlit dashboard:

```bash
streamlit run app.py
```

The application opens in your web browser at `http://localhost:8501`.

### Navigating the Multi-Page Application:
The application uses modular views located in `src/ui/`:
1. **🏠 Home / Dashboard (`src/ui/home_page.py`):** Executive overview, live collection count metric (9,532), embedding model specs, and architecture flowchart.
2. **🔧 Troubleshooting Assistant (`src/ui/assistant_page.py`):** Interactive diagnostic interface. Enter symptoms or select from Q01–Q10 presets. Supports live Ollama LLM or offline Mock provider, citation inspection cards, and safety alert banners.
3. **🔍 Semantic Search (`src/ui/search_page.py`):** Direct semantic search across 9,532 records with subsystem domain and severity dropdown filters, displaying similarity scores and complete metadata.
4. **📊 Evaluation Dashboard (`src/ui/evaluation_page.py`):** Interactive visualization of Phase 4 top-K rankings, Phase 5 similarity comparison metrics, and Phase 6.1 RAG vs baseline results.
5. **📖 About / Dataset (`src/ui/about_page.py`):** Provenance documentation, schema specification, subsystem and severity distributions.

---

## 6. Running Headless Experimentation Scripts

All research experiments can be re-run independently from the command line:

### 6.1 Semantic Search & Metadata Filter Evaluation (Phase 4)
```bash
python scripts/run_queries.py
# Executes Top-5 and Top-10 retrieval across Q01–Q10 plus 5 compound metadata filters
# Results saved to: experiments/semantic_search_results.json and metadata_filter_results.json
```

### 6.2 Mathematical Similarity Comparison (Phase 5)
```bash
python scripts/run_similarity_comparison.py
# Computes 60 evaluations across Euclidean, Cosine, and Dot Product using pure vectorized NumPy
# Proves rank equivalence on unit vectors and demonstrates unnormalized synthetic divergence
# Results saved to: experiments/similarity_comparison_results.json
```

### 6.3 Retrieval-Augmented Generation (RAG) Evaluation (Phase 6)
```bash
# Mode 1: Deterministic Offline Mock (instant, zero GPU/LLM required):
python scripts/run_rag.py --mode mock

# Mode 2: Real Local LLM (requires Ollama running with llama3.2):
python scripts/run_rag.py --mode real
# Evaluates 10 RAG + 10 Baseline queries; computes citation precision and recall
# Results saved to: experiments/rag_real_results.json and rag_real_evaluation.csv
```

### 6.4 Optional: Re-prepare Processed Dataset from Source
```bash
python scripts/prepare_dataset.py
# Validates and normalizes raw records into data/processed/vehicle_troubleshooting.json
```
