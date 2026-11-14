# System Architecture — Vehicle Troubleshooting Assistant

**Course:** Modern Database Systems (Assignment 2)  
**Academic Institution:** BITS Pilani WILP  
**Group:** 20  

---

## 1. Architectural Overview

The **Vehicle Troubleshooting Assistant** follows a decoupled, pipeline-oriented architecture designed to separate data ingestion, dense vector indexing, similarity benchmarking, grounded generative synthesis, automotive domain safety validation, and user interface delivery.

```mermaid
flowchart TD
    subgraph Layer 1: Data Ingestion & Preprocessing
        Raw["Raw Public Data (Zenodo 15626055, OBDex)"] --> Pre["src/preprocessing.py\nNormalization & Schema Standardization"]
        Pre --> Val["src/dataset_validator.py\nSchema, Uniqueness & Quality Validation"]
        Val --> JSON["data/processed/vehicle_troubleshooting.json\n(9,532 Validated Records)"]
    end

    subgraph Layer 2: Embedding & Persistent Vector Storage
        JSON --> Emb["src/embeddings.py (EmbeddingEngine)\nsentence-transformers/all-MiniLM-L6-v2\n384-dim Float32, L2 Unit-Normalized"]
        Emb --> Chroma[("database/chroma_db/chroma.sqlite3\nCollection: vehicle_troubleshooting_kb\nHNSW Index (Cosine Space)")]
        Emb --> NpMatrix["src/numpy_similarity.py (NumpySimilarityEngine)\nExhaustive 9,532x384 Dense Matrix"]
    end

    subgraph Layer 3: Retrieval & Mathematical Validation
        Query["Driver Complaint / Technical Symptom"] --> QEmb["Query Vector (384-dim, Normalized)"]
        QEmb -->|Approximate kNN O(log N)| Chroma
        Chroma --> Ret["Retrieved Top-K Passages + Metadata"]
        QEmb -->|Exhaustive Linear Scan O(N)| NpMatrix
        NpMatrix --> Comp["Mathematical Proof & Metric Comparison\n(Euclidean vs. Cosine vs. Dot Product)"]
    end

    subgraph Layer 4: Safety & Generation Layer
        Ret --> Safe["src/safety_guardrails.py (SafetyGuardrailEngine)\nInterceptors: SRS, High-Voltage, Brakes, Cooling, 12V vs EV"]
        Safe --> Prompt["Prompt Assembly (v2.2.0)\nContext Formatting & Anti-Hallucination Directives"]
        Prompt --> LLM["src/llm_provider.py\nOllamaProvider (Llama 3.2 3B) / MockLLMProvider"]
        LLM --> Gen["Grounded Report with In-Text Citations [VTR-XXXXX]"]
    end

    subgraph Layer 5: Presentation & Interface
        Gen --> UI["app.py & src/ui/\nMulti-Page Streamlit Application"]
        Ret --> UI
        Safe --> UI
    end
```

---

## 2. Layer-by-Layer Architectural Breakdown

### 2.1 Layer 1: Data Ingestion & Preprocessing
- **Source Ingestion:** `src/dataset_loader.py` reads raw diagnostic records from `data/raw/obdex/` and public Zenodo candidate tables.
- **Normalization:** `src/preprocessing.py` standardizes vehicle subsystems into four canonical categories (`engine_and_transmission`, `brakes_and_suspension`, `electrical_and_body`, `network_and_communication`), normalizes severity classifications (`critical`, `high`, `medium`, `low`), cleans noisy formatting, and generates the composite document string used for vectorization.
- **Validation:** `src/dataset_validator.py` enforces mandatory fields (`record_id`, `diagnostic_codes`, `title`, `vehicle_system`, `severity`, `symptoms`, `probable_causes`, `diagnostic_steps`, `safety_warnings`, `document`), checks for zero synthetic duplicates, and confirms the volume threshold ($\ge 5,000$).

### 2.2 Layer 2: Embedding & Persistent Vector Storage
- **Embedding Generation:** `src/embeddings.py` loads `sentence-transformers/all-MiniLM-L6-v2`. Each record's composite text is mapped to a 384-dimensional dense vector and immediately $L_2$-normalized to unit magnitude ($\|\mathbf{x}\|_2 = 1.0$).
- **Persistent ChromaDB Manager:** `src/chroma_manager.py` initializes a persistent ChromaDB client pointing to `database/chroma_db/`. The collection `vehicle_troubleshooting_kb` is configured with `hnsw:space = "cosine"`.
- **CRUD Operations:** `src/crud_operations.py` implements Create, Read, Update, and Delete operations for individual records. Automated tests in `tests/test_chroma.py` execute CRUD cycles using isolated sandbox IDs (`TEST-CRUD-XXXX`) with mandatory teardown, ensuring the 9,532 production records remain untouched.

### 2.3 Layer 3: Retrieval & Mathematical Validation
- **Semantic Search Engine:** `src/semantic_search.py` converts natural language queries to dense vectors and queries ChromaDB using approximate nearest neighbor (ANN) search via HNSW graphs.
- **Metadata Filter Engine:** `src/metadata_filters.py` constructs single and compound boolean `$and` filters targeting `vehicle_system` and `severity`.
- **Pure NumPy Similarity Engine:** `src/numpy_similarity.py` loads all 9,532 database embeddings into an $(N \times 384)$ float32 NumPy array and executes exact linear-scan searches for all 10 benchmark queries across Euclidean distance ($L_2$), Cosine similarity, and Dot product.

### 2.4 Layer 4: Safety & Generation Layer
- **Safety Guardrail Engine:** `src/safety_guardrails.py` acts as a pre-generation and post-retrieval middleware. It checks both the user query and the retrieved context documents against safety rules:
  1. **SRS Airbag Circuits:** Prohibits ohmmeter probing across squibs and clarifies that battery disconnection is not sufficient by itself.
  2. **High-Voltage EV/Hybrid:** Issues lethal shock warnings (300V–800V) and mandates certified technician lockout/tagout.
  3. **Hydraulic Brake Failure:** Detects sinking brake pedal symptoms, enforces a mandatory **DO NOT DRIVE** warning, and mandates towing.
  4. **Cooling System Scald:** Warns against opening hot or pressurized cooling systems and forbids unsafe upper-radiator-hose squeezing instructions.
  5. **12V ICE vs. EV Domain Mismatch:** Flags queries where an ordinary 12V alternator drain retrieves high-voltage EV battery charger codes.
- **RAG Pipeline:** `src/rag_pipeline.py` formats retrieved documents into structured context blocks, applies system prompt template `v2.2.0-grounded-automotive-diagnostic`, enforces source attribution (`[VTR-XXXXX]`), calls the configured LLM provider, extracts citations, and computes latency.
- **LLM Provider Abstraction:** `src/llm_provider.py` provides an abstract base class (`BaseLLMProvider`) with three implementations:
  1. `OllamaProvider`: Connects to a local Ollama daemon hosting Meta Llama 3.2 (3B).
  2. `OpenAICompatibleProvider`: Connects to external OpenAI-compatible endpoints.
  3. `MockLLMProvider`: Deterministic fallback provider for offline CI testing and environments where no LLM daemon is running.

### 2.5 Layer 5: Presentation & Interface
- **Streamlit Application:** `app.py` and `src/ui/` provide a 5-page interactive dashboard:
  - **Page 1 (`home_page.py`):** System architecture overview, dynamic KPI metrics, and subsystem breakdown.
  - **Page 2 (`assistant_page.py`):** Interactive grounded troubleshooting assistant with benchmark presets, safety banners, and markdown report download.
  - **Page 3 (`search_page.py`):** Vector search explorer with compound metadata filters, diagnostic cards, and CSV export.
  - **Page 4 (`evaluation_page.py`):** Empirical benchmarks, Plotly comparative charts, and side-by-side RAG vs. baseline inspector.
  - **Page 5 (`about_page.py`):** Dataset provenance documentation, schema specification, and interactive Plotly distribution charts.

---

## 3. Concurrency and Persistence Strategy

- **Local Persistence:** ChromaDB writes metadata directly to `database/chroma_db/chroma.sqlite3`. This file is completely self-contained and does not require an external database service.
- **Streamlit Resource Caching:** Expensive objects (the ChromaDB client, the sentence-transformer neural network weights, and the RAG pipeline) are wrapped in `@st.cache_resource(show_spinner=False)`. This ensures that weights are loaded into memory exactly once per session, allowing page transitions and query evaluations to respond with sub-second retrieval latency.
