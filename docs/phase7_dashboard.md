# Phase 7 Dashboard Architecture & User Guide

**Project Title:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Course:** BITS Pilani WILP — Modern Database Systems (Assignment 2)  
**Document:** Streamlit Multi-Page Web Application Architecture and Operator Manual  
**Component:** `app.py`, `src/ui/`, `src/safety_guardrails.py`  
**Status:** Implemented, Tested, and Verified (68/68 Automated Tests Passing)  

---

## 1. Executive Summary

Phase 7 delivers a responsive, academic-grade Streamlit web application for the Vehicle Troubleshooting Assistant. The interface operationalizes the underlying 9,532-record persistent ChromaDB vector store, the sentence-transformers dense embedding model (`all-MiniLM-L6-v2`), the grounded RAG generation pipeline, and local neural inference via Ollama Meta Llama 3.2.

The application adheres strictly to academic evaluation standards, providing:
1. **Grounded Diagnostic Assistant**: With vehicle type selection (ICE, Hybrid, EV, Unknown), top-K control, max token adjustments, and prominent backend safety guardrail banners.
2. **Semantic Search Explorer**: With multi-condition compound metadata filtering ($and logic across subsystems and severity), distance/similarity reporting, and expandable document cards.
3. **Multi-Phase Empirical Evaluation Dashboard**: Displaying historical benchmarks from Phase 4 (retrieval distributions), Phase 5 (NumPy L2 vs. Cosine vs. Dot Product comparisons), and Phase 6.1 (Real LLM generation, citation fidelity, and latency analysis).
4. **Dataset Provenance & Boundary Disclosure**: Documenting CC0 1.0 open-access origins, preprocessing pipelines, and distinguishing source diagnostic data from generative suggestions.

---

## 2. Multi-Page Application Architecture

```
app.py (Streamlit Entrypoint & Routing Hub)
 │
 ├── Sidebar Navigation & System Telemetry (src/ui/components.py)
 │    ├── ChromaDB Collection Count Badge (9,532 records)
 │    ├── Embedding Dimensions Badge (384-dim, all-MiniLM-L6-v2)
 │    ├── Active Provider Indicator (Ollama llama3.2:latest / Mock fallback)
 │    └── Academic Attribution (BITS Pilani WILP Assignment 2)
 │
 ├── Page 1: 🏠 Home / Dashboard (src/ui/home_page.py)
 │    ├── Key Performance Metrics (Indexed records, dimensions, LLM, benchmark queries)
 │    ├── Project Objective & Anti-Hallucination Motivation
 │    ├── Five Operational Automotive Safety Guardrails
 │    └── Interactive RAG Flowchart Diagram
 │
 ├── Page 2: 🔧 Vehicle Troubleshooting Assistant (src/ui/assistant_page.py)
 │    ├── One-Click Benchmark Preset Buttons (Q01, Q03, Q04, Q09, Q10)
 │    ├── Symptom Input & Vehicle Powertrain Selector (ICE / Hybrid / EV / Unknown)
 │    ├── Optional Metadata (Make, Model, Year, Engine)
 │    ├── Tunable Parameters (Retrieval Cutoff K: 1-10, Max Output Tokens: 512-2048)
 │    ├── Prominent Automotive Safety Banners (SRS squib hazards, 400V EV loops, braking)
 │    ├── Domain Mismatch Alert (e.g. 12V ICE alternator drain vs. EV charger codes)
 │    ├── Structured Grounded Answer with [VTR-XXXXX] Verified Source Badges
 │    └── Retrieved Diagnostic Knowledge Cards (Distances, Similarities, Full Excerpts)
 │
 ├── Page 3: 🔍 Semantic Search Explorer (src/ui/search_page.py)
 │    ├── Dense Vector Natural Language Query Input
 │    ├── Top-K Cardinality Slider (1 to 25)
 │    ├── Compound Metadata Filters (Vehicle Subsystem & Severity Dropdowns)
 │    ├── Card View vs. Interactive Tabular Dataframe View
 │    └── Raw Document Excerpt Inspection Accordions
 │
 ├── Page 4: 📊 Empirical Evaluation Dashboard (src/ui/evaluation_page.py)
 │    ├── Tab 1: Phase 6.1 Real RAG vs. Baseline Benchmark Table (Q01–Q10)
 │    ├── Side-by-Side Response Inspector (Grounded RAG vs. Unassisted Baseline)
 │    ├── Tab 2: Citation Fidelity & Reference Provenance vs. Factual Truth Analysis
 │    ├── Tab 3: Phase 5 NumPy Metric Comparisons (L2 vs. Cosine vs. Dot Product)
 │    └── Tab 4: Phase 4 Dense Retrieval Top-K Benchmark Tables
 │
 └── Page 5: 📖 About & Dataset Provenance (src/ui/about_page.py)
      ├── Zenodo (15626055) & OBDex Knowledge Base Provenance (CC0 1.0 License)
      ├── Category & Severity Distribution Tables & Interactive Bar Charts
      ├── Technical End-to-End Stack Diagram
      └── Correlation vs. Causation Boundaries in OBD-II Diagnostics
```

---

## 3. Backend Automotive Safety Controls

Automotive troubleshooting carries critical physical safety hazards. The application implements backend validation in `src/safety_guardrails.py` and `src/rag_pipeline.py`:

### A. Supplemental Restraint Systems (SRS / Airbag)
- **Targeted Trigger**: Detects airbag, clock spring, squib, deployment loop, and B0001–B0099 codes. (Does not trigger merely on generic non-SRS B-codes like HVAC B0223).
- **Mandatory Directive**: Forbids ohmmeter/multimeter testing across squib terminals (meter current triggers pyrotechnic detonation). Disallows external voltage and unverified wiring pinouts.
- **UI Banner**: Displays a prominent **DANGER** banner instructing battery disconnect and factory manual compliance.

### B. High-Voltage Hybrid & Electric Vehicle Systems
- **Targeted Trigger**: Detects hybrid, EV, high voltage, HVIL, inverter, and P0B/P0C/P0D codes.
- **Mandatory Directive**: Warns against touching orange cables or opening traction battery enclosures without Class-0 (1,000V) gloves and lockout/tagout.
- **UI Banner**: Displays a prominent **DANGER** banner emphasizing lethal 300V–800V DC potentials.

### C. ICE 12V Battery Drain vs. EV Charger Mismatch
- **Targeted Trigger**: Triggered when an ICE vehicle (or query mentioning an alternator) with a dead battery retrieves EV charger/HVIL codes (`P0D17`, `P0D46`).
- **Correction**: Warns the user and instructs the LLM not to attribute ordinary 12V battery drains to EV high-voltage loops. Instructs standard 12V parasitic draw testing (fuse millivolt-drop test).

### D. Hydraulic Braking System Safety
- **Targeted Trigger**: Detects sinking pedal, pedal to floorboard, soft pedal, or hydraulic loss.
- **Mandatory Directive**: Classifies vehicle as **UNSAFE TO DRIVE** (catastrophic stopping failure risk). Mandates immediate towing to an ASE-certified repair shop. Never implies ABS codes guarantee hydraulic safety.

### E. Engine Cooling & Thermal Scald Hazards
- **Targeted Trigger**: Detects boiling coolant, rapid overheating, or steam.
- **Mandatory Directive**: Warns never to open a hot, pressurized radiator cap or reservoir (explosive steam and scald burn hazard). Mandates 45-minute cool-down period.

---

## 4. How to Start the Streamlit Application

### Step 1: Ensure Prerequisites are Active
```bash
# Verify local virtual environment
source .venv/bin/activate

# (Optional for live LLM) Ensure Ollama daemon is running with Llama 3.2
ollama list
# Should list: llama3.2:latest
```

### Step 2: Launch Application
```bash
# Launch Streamlit with local network binding
streamlit run app.py
```
The application will start immediately at `http://localhost:8501`.

---

## 5. Performance and Responsiveness Optimizations

1. **Singleton Resource Caching (`st.cache_resource`)**:
   - `get_cached_chroma_manager()`: ChromaDB persistent connection is opened once and reused across page switches.
   - `get_cached_search_engine()`: SentenceTransformer model weights (`all-MiniLM-L6-v2`) remain warm in memory, eliminating redundant reload overhead.
   - `get_cached_rag_pipeline()`: Provider abstraction and retrieval engines are cached as singletons.
2. **Data Caching (`st.cache_data`)**:
   - Historical evaluation CSVs and JSON result files are cached in memory.
   - Dataset distribution aggregations are cached after first calculation.
3. **Configurable Token Limit & Truncation Handling**:
   - Tunable max tokens slider (default: 1,536 tokens).
   - If a generation reaches the token limit, the UI surfaces a clear warning: *"Response Truncated: Model output reached the configured token limit"*, preventing partial answers from masquerading as complete diagnoses.
