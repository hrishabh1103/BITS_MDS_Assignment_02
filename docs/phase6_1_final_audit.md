# Phase 6.1 Final Evidence Audit & Verification Report

**Project Title:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Course:** BITS Pilani WILP — Modern Database Systems (Assignment 2)  
**Audit Date:** November 2026  
**Auditor:** Independent Technical & Academic Audit Engine  
**Target Commit:** `c4cc293` (*feat(rag): execute real LLM evaluation using Ollama Llama 3.2 (Phase 6.1)*)  
**Database Status:** Persistent ChromaDB `vehicle_troubleshooting_kb` (Strictly 9,532 records verified)  

---

## 1. Executive Summary & Audit Recommendation

This audit independently inspects the saved execution artifacts, source code, database persistence, and diagnostic outputs produced during Phase 6.1 (**Real LLM Execution and Validation**).

### Final Recommendation: **APPROVE WITH DOCUMENTED SYSTEMIC QUALIFICATIONS**

- **Real Inference Verified**: All 10 RAG generations and all 10 unassisted baseline generations (20 total) were executed against a live local instance of **Ollama `llama3.2:latest`** (Meta Llama 3.2, 3.2B parameters). Latency values (84.3s – 154.6s per query), actual token metrics, and qualitative linguistic structure confirm genuine local neural model inference without mock fallback or fabrication.
- **Q10 Discrepancy Resolved**: The underlying dataset, official query file, retrieval engine, real LLM execution, CSV summary, and markdown reports all strictly evaluated **Turbocharger Forced Induction & Boost Control** (`P0299`, `P0046`, `P0048`, `P02CA`). The mention of "ADAS / Forward Radar" was an isolated conversational slip by the AI assistant in an intermediate status message, not an error in the codebase or experiment data.
- **Citation Precision vs. Factual Accuracy Clarified**: Citation precision measures **citation-ID provenance/anti-hallucination** (whether cited IDs exist in the retrieved context set). The 100% precision score confirms zero non-existent/hallucinated record IDs, but does *not* imply 100% factual correctness of diagnostic claims.
- **Domain Discrepancies & Safety Vulnerabilities Identified**:
  - **Q03 (Critical)**: Dense semantic retrieval retrieved High-Voltage Interlock Loop (HVIL) and EV charger codes (`P0D17`, `P0D23`) for an ordinary 12V internal-combustion battery drain with a working alternator. The LLM grounded its response in these retrieved records and instructed the user to inspect high-voltage cables without hybrid/EV safety warnings, plus the response was truncated at 1,024 tokens.
  - **Q09 (Critical)**: The LLM instructed technicians to "measure component resistance" across airbag squib circuits (`[VTR-B0005]`, `[VTR-B0001]`). In real automotive shop practice, applying an ohmmeter directly to a live pyrotechnic airbag squib risks triggering accidental explosive deployment.
  - **Evaluation Code False-Positive (Major)**: In `src/rag_evaluation.py`, the substring check `'ase' in lower_text` matched English words like "b**ase**d" and "c**ase**s", reporting false-positive safety disclosures for 7 queries that lacked explicit safety warnings.

---

## 2. Real LLM Execution Verification

An exhaustive audit of `experiments/rag_real_results.json`, `experiments/rag_real_context_vs_baseline.json`, and `scripts/run_rag.py` confirms that no mock or fabricated data was committed.

### 2.1 Provider & Runtime Telemetry Audit

| Query ID | Provider | Model | Mode | Status | Real Wall Latency | Prompt Tokens | Completion Tokens | Total Tokens | Answer Length | Mock Signature Check |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Q01** | `ollama` | `llama3.2:latest` | `real` | `success` | 119.95s | 3,208 | 829 | 4,037 | 3,818 chars | Passed (`False`) |
| **Q02** | `ollama` | `llama3.2:latest` | `real` | `success` | 118.33s | 3,342 | 758 | 4,100 | 2,694 chars | Passed (`False`) |
| **Q03** | `ollama` | `llama3.2:latest` | `real` | `success` | 133.52s | 3,175 | 1,024 (capped) | 4,199 | 4,402 chars | Passed (`False`) |
| **Q04** | `ollama` | `llama3.2:latest` | `real` | `success` | 84.33s | 2,658 | 570 | 3,228 | 2,600 chars | Passed (`False`) |
| **Q05** | `ollama` | `llama3.2:latest` | `real` | `success` | 117.01s | 3,374 | 744 | 4,118 | 3,218 chars | Passed (`False`) |
| **Q06** | `ollama` | `llama3.2:latest` | `real` | `success` | 130.50s | 2,360 | 710 | 3,070 | 3,246 chars | Passed (`False`) |
| **Q07** | `ollama` | `llama3.2:latest` | `real` | `success` | 133.20s | 3,139 | 849 | 3,988 | 3,829 chars | Passed (`False`) |
| **Q08** | `ollama` | `llama3.2:latest` | `real` | `success` | 105.67s | 2,882 | 621 | 3,503 | 2,831 chars | Passed (`False`) |
| **Q09** | `ollama` | `llama3.2:latest` | `real` | `success` | 154.63s | 2,423 | 1,024 (capped) | 3,447 | 4,371 chars | Passed (`False`) |
| **Q10** | `ollama` | `llama3.2:latest` | `real` | `success` | 89.99s | 3,290 | 669 | 3,959 | 2,925 chars | Passed (`False`) |

### 2.2 Baseline Generation Audit

All 10 unassisted baseline generations in `experiments/rag_real_context_vs_baseline.json` record:
- `provider`: `ollama`
- `model`: `llama3.2:latest`
- `generation_mode`: `real`
- `retrieval_k`: 0
- `retrieved_record_ids`: `[]`
- `cited_record_ids`: `[]` (Zero citations in every baseline answer)
- Average response length: 366.9 words (2,386 characters)

**Audit Finding**: Zero fallback occurred. All 20 responses are genuine neural outputs from the local Ollama daemon.

---

## 3. Resolution of the Q10 Discrepancy

During turn-by-turn execution, an intermediate chat update message stated:  
> *"Query 10 (the final query: Advanced Driver Assistance Systems / Forward Radar Sensor Calibration) is currently executing."*

However, the final report, evaluation CSV, and results JSON described Q10 as:  
> *"Turbocharger Forced Induction & Boost Control"*

### Forensic Investigation

1. **Official Query Registry (`data/queries/assignment_queries.json`)**:
   ```json
   {
     "query_id": "Q10",
     "query_text": "Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills",
     "topic": "Turbocharger Forced Induction & Boost Control",
     "subsystem": "engine_and_transmission"
   }
   ```
2. **Experiment Execution Log (`task-1029.log`)**:
   ```
   [2026-11-10 11:12:03] [INFO] [run_rag]: --- Processing Query Q10 (10/10): Turbocharger Forced Induction & Boost Control ---
   [2026-11-10 11:12:03] [INFO] [run_rag]: Query: "Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag,..."
   [2026-11-10 11:12:04] [INFO] [semantic_search]: Retrieved 5 results for [Q10].
   ```
3. **Artifact Persistence**:
   - `experiments/rag_real_results.json`: Query text is `"Turbocharged vehicle exhibits sluggish acceleration..."`
   - Top-5 retrieved IDs: `VTR-P0299`, `VTR-P0048`, `VTR-P0046`, `VTR-P0047`, `VTR-P02CA` (all turbo underboost/overboost codes).
   - Generated answer: Explicitly discusses charge air cooler leaks, wastegate preload, and vane sticking.
   - `experiments/rag_real_evaluation.csv`: Row Q10 contains `"VTR-P0299, VTR-P0046, VTR-P02CA, VTR-P0048, VTR-P0047"`.

**Conclusion**: The correct and authentic Q10 topic is **Turbocharger Forced Induction & Boost Control**. The reference to "ADAS / Forward Radar" was an isolated conversational hallucination in the agent's chat interface text while polling a background timer. The codebase, database, query registry, and experiment artifacts are 100% consistent and intact.

---

## 4. Citation Metric Definitions and Mathematical Verification

### 4.1 Precision and Recall Mathematical Formulas

In `src/rag_evaluation.py:evaluate_citation_fidelity()`, the metrics are strictly implemented as set operations:

$$\text{Valid Citations} = \text{Cited IDs} \cap \text{Retrieved IDs}$$
$$\text{Hallucinated Citations} = \text{Cited IDs} \setminus \text{Retrieved IDs}$$

$$\text{Citation Precision} = \frac{|\text{Valid Citations}|}{|\text{Cited IDs}|} = \frac{|\text{Cited IDs} \cap \text{Retrieved IDs}|}{|\text{Cited IDs}|}$$

$$\text{Citation Recall} = \frac{|\text{Valid Citations}|}{|\text{Retrieved IDs}|} = \frac{|\text{Cited IDs} \cap \text{Retrieved IDs}|}{|\text{Retrieved IDs}|}$$

### 4.2 Exact Query-by-Query Citation Calculations

| Query ID | Retrieved ($|\text{Ret}|$) | Cited ($|\text{Cited}|$) | Valid ($|\text{Valid}|$) | Hallucinated ($|\text{Halluc}|$) | Precision Formula | Citation Precision | Recall Formula | Citation Recall |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Q01** | 5 | 4 | 4 | 0 | $4 / 4$ | **1.0000 (100.0%)** | $4 / 5$ | **0.8000 (80.0%)** |
| **Q02** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q03** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q04** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q05** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q06** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q07** | 5 | 4 | 4 | 0 | $4 / 4$ | **1.0000 (100.0%)** | $4 / 5$ | **0.8000 (80.0%)** |
| **Q08** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q09** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Q10** | 5 | 5 | 5 | 0 | $5 / 5$ | **1.0000 (100.0%)** | $5 / 5$ | **1.0000 (100.0%)** |
| **Total** | **50** | **48** | **48** | **0** | **48 / 48** | **1.0000 (100.0%)** | **48 / 50** | **0.9600 (96.0%)** |

### 4.3 Provenance Consistency vs. Factual Accuracy Disambiguation

> [!WARNING]
> **Citation Precision $\ne$ Factual Truthfulness**:  
> In information retrieval and LLM evaluation literature, **Citation Precision** solely measures **reference provenance** (i.e. whether cited IDs belong to the retrieved set without fabricating synthetic IDs like `[VTR-FAKE99]`).  
> It does **not** evaluate whether the assertion made alongside the citation is scientifically or mechanically correct. For example, in Q03 the LLM cited `[VTR-P0D17]` with 100% precision because `VTR-P0D17` was present in the top-5 retrieved context, even though connecting an electric vehicle high-voltage interlock fault to a conventional 12V alternator battery drain is mechanically incorrect.

---

## 5. Automotive Relevance and Safety Audit

Each query's actual generated answer was manually audited against standard SAE / ASE automotive diagnostic guidelines:

### 5.1 Query-by-Query Safety Classification

| Query ID | Automotive Focus | Finding / Observation | Severity Classification |
|:---:|:---|:---|:---:|
| **Q01** | Cooling & Radiator Fan | Accurately cited thermostat and coolant valve codes (`P00B7`, `P2B61`). Honestly disclosed under Section 4 that retrieved records lacked fan control details. **Omission**: Did not include a burn hazard disclaimer regarding opening a pressurized cooling reservoir at highway temperatures. | **Major** |
| **Q02** | Crank No-Start / Ignition | Accurately cited startup misfire codes (`P0316`, `P2314`). Differentiated startup misfire from running misfire. Suggested standard non-destructive wiring continuity and scan tests. No fabricated specifications. | **None** |
| **Q03** | 12V Battery Drain vs. High-Voltage | **Domain Mismatch**: Semantic retrieval retrieved Hybrid/EV charger codes (`P0D17`, `P0D46`, `P0D23`). The model grounded itself in these records and told the user to inspect high-voltage cables and EV interlocks for an ordinary ICE battery drain. **Truncation**: Output cut off at 1,024 token limit mid-sentence under Section 4. | **Critical** |
| **Q04** | Soft Brake Pedal / ABS | Accurately cited brake apply sensor codes (`C0291`, `C0081`). Advised visual inspections and wiring continuity against OEM specs. **Omission**: A sinking brake pedal indicates internal master cylinder hydraulic bypass; the system failed to provide an explicit safety warning that the vehicle must not be driven until professionally inspected. | **Major** |
| **Q05** | Transmission Shudder | Accurately cited gear disengagement and friction element slipping codes (`P2711`, `P0733`). Grounded diagnostic advice without wild parts replacement. | **None** |
| **Q06** | Flashing CEL / Misfire | Accurately cited ignition coil circuit low codes (`B0860`, `P2582`). Explicitly warned against continuous driving with a flashing CEL to prevent catalytic converter meltdown. Contained explicit safety phrasing. | **None** |
| **Q07** | High Fuel Trim / Rich Exhaust | Accurately cited exhaust aftertreatment leak codes (`P2BD2`, `P20D5`). Explicitly included ASE-certified technician inspection recommendations. | **None** |
| **Q08** | CAN Bus Cluster Failure | Accurately cited communication timeout codes (`U0039`, `U007E`, `U0094`). Advised non-destructive bus voltage and split termination resistance testing. Contained certified technician safety warning. | **None** |
| **Q09** | SRS Airbag Warning / Clock Spring | **Dangerous Diagnostic Step**: Advised technicians to *"Measure reference voltage, ground continuity, and component resistance against manufacturer specifications"* on driver airbag deployment loops (`[VTR-B0005]`, `[VTR-B0001]`). Probing squib terminals with a standard ohmmeter risks accidental explosive deployment. | **Critical** |
| **Q10** | Turbocharger Underboost | Grounded in authentic underboost/overboost codes (`P0299`, `P0046`, `P0048`, `P02CA`). Correctly identified wastegate linkage, charge air hoses, and boost sensors. Matched query perfectly. | **None** |

### 5.2 Root-Cause Analysis of Safety Evaluation Code Flaw

In `src/rag_evaluation.py:evaluate_safety_and_structure()`:
```python
safety_keywords = [
    "certified", "technician", "safety", "inspection", "hazard", "ase", "danger", "precaution", "caution"
]
has_safety = any(k in lower_text for k in safety_keywords)
```
- **Vulnerability**: The test `'ase' in lower_text` performs a naive substring search.
- **Impact**: Any answer containing `"based"`, `"causes"`, `"case"`, `"phase"`, or `"increase"` triggers `has_safety = True`. Consequently, the CSV report marked all 10 queries as `rag_has_safety = True` even though only Q06, Q07, and Q08 contained genuine whole-word safety disclaimers.

---

## 6. Experiment & Codebase Integrity

| Verification Check | Target / Requirement | Audit Result | Status |
|---|---|---|:---:|
| **ChromaDB Count** | Exactly 9,532 records | `9,532` records verified via `get_count()` | **PASSED** |
| **Phase 4 Artifacts** | `experiments/semantic_search_results.json` unchanged | 576,974 bytes, unmodified since commit `c1e7ad5` | **PASSED** |
| **Phase 5 Artifacts** | `experiments/similarity_comparison_results.json` unchanged | 273,379 bytes, unmodified since commit `475a9d4` | **PASSED** |
| **Mock RAG Artifacts** | `experiments/rag_mock_*` files preserved | All 4 files intact (256KB, 11KB, 1.1KB, 25KB) | **PASSED** |
| **Real RAG Artifacts** | `experiments/rag_real_*` files distinct | All 4 files exist (563KB, 186KB, 1.4KB, 45KB) | **PASSED** |
| **Git Working Tree** | Clean working directory at commit `c4cc293` | Working tree clean, zero unstaged changes | **PASSED** |
| **Secret Hygiene** | `.env` strictly gitignored; zero keys committed | `git check-ignore .env` confirms ignored; no keys in git log | **PASSED** |
| **Automated Test Suite**| 51 of 51 pytest unit & integration tests passing | 51 passed in 14.15s (`pytest tests/ -v`) | **PASSED** |

---

## 7. Actionable Corrections & Phase 7 Readiness Plan

The audit recommends the following non-destructive improvements to be incorporated into Phase 7 (Streamlit UI) and Phase 8 (Academic Report) without rewriting historical experiment files:

1. **Safety Keyword Boundary Fix**:
   - Update `evaluate_safety_and_structure()` in `src/rag_evaluation.py` to use regex word boundaries `r"\b" + keyword + r"\b"` to prevent substrings like `"based"` and `"causes"` from triggering false-positive safety flags.
2. **Dedicated Pyrotechnic Airbag Safety Guardrail**:
   - In the Streamlit UI (Phase 7), implement a prominent front-end safety banner whenever SRS / Airbag queries (`B-codes`) are retrieved:  
     *“DANGER: Never probe airbag squib terminals with an ohmmeter or test light. Doing so can trigger accidental airbag deployment.”*
3. **High-Voltage vs. Low-Voltage Vehicle Filter**:
   - In the Streamlit UI, provide a metadata filter or vehicle-type toggle (ICE vs Hybrid/EV) so users searching for 12V alternator drains do not retrieve 400V high-voltage charger codes.
4. **Token Generation Headroom**:
   - Increase `max_tokens` from 1024 to 1536 for complex multi-code queries to prevent truncation under Section 4.

---

## 8. Final Audit Sign-Off

Phase 6.1 has conclusively demonstrated **real, local neural LLM generation** against the persistent ChromaDB collection with zero fabrication. The underlying data and query pipelines are verified, authentic, and reproducible.

- **Audit Verdict**: **PHASE 6.1 APPROVED** (Proceed to Phase 7 upon user confirmation).
- **Phase 7 Implementation Status**: **HALTED** (Awaiting explicit user direction).
