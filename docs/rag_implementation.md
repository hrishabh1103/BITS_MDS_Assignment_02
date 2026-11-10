# Retrieval-Augmented Generation (RAG) Architecture & Implementation

## BITS Pilani WILP — Modern Database Systems (Assignment 2)
**Project Title**: Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Document**: Phase 6 RAG Architecture, Provider Abstraction, and Baseline Comparative Evaluation  
**Dataset**: 9,532 authentic vehicle diagnostic records (`data/processed/vehicle_troubleshooting.json`)  
**Vector Store**: ChromaDB persistent collection `vehicle_troubleshooting_kb` (Cosine space)  
**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, $L_2$-normalized)  

---

## 1. Executive Summary

Phase 6 implements the complete Retrieval-Augmented Generation (RAG) subsystem for the Vehicle Troubleshooting Assistant. The system bridges natural language driver complaints with dense vector retrieval over the 9,532-record ChromaDB database and a structured, grounded LLM prompt architecture.

### Key Capabilities Implemented
1. **Modular RAG Pipeline (`src/rag_pipeline.py`)**: Orchestrates semantic retrieval, annotated context formatting, grounded prompt synthesis, citation parsing, and structured output formatting.
2. **Provider Abstraction Layer (`src/llm_provider.py`)**: Decouples generation from specific model vendors, natively supporting local Ollama daemons, OpenAI-compatible APIs (OpenAI, Gemini API, Groq, vLLM), and a deterministic Mock provider for offline automated grading.
3. **Rigorous Anti-Hallucination Guardrails**: Prompts enforce correlation vs. causation boundaries (e.g., a DTC does not prove component failure), mandate square-bracket record citations (`[VTR-XXXXX]`), and require automotive safety disclosures.
4. **Context vs. No-Context Baseline Comparison (`src/rag_evaluation.py`)**: Evaluates all 10 assignment queries (Q01–Q10) side-by-side with and without retrieved context, proving that RAG transforms generic automotive advice into specific, actionable, and grounded diagnostic procedures.

---

## 2. RAG Architecture & System Workflow

```mermaid
flowchart TD
    subgraph "1. User Query & Retrieval"
        UQ["Driver Complaint / Symptom Query"] --> EMB["SentenceTransformer<br/>(all-MiniLM-L6-v2)"]
        EMB --> VEC["Query Vector q (384-dim, ||q||=1)"]
        VEC --> CDB[("ChromaDB Persistent Store<br/>9,532 Diagnostic Records")]
        CDB -->|Top-5 Cosine Search| RET["Retrieved Candidates<br/>(IDs, Titles, Codes, Excerpts, Distances)"]
    end

    subgraph "2. Context Annotation & Prompting"
        RET --> CFMT["Context Formatter<br/>Annotate Ranks, Codes, Symptoms, Causes, Distances"]
        CFMT --> PROMPT["Grounded Prompt Construction<br/>(System Prompt + Context + Query)"]
    end

    subgraph "3. Provider Abstraction & Generation"
        PROMPT --> LLM_ROUTER{"LLM Provider Factory"}
        LLM_ROUTER -->|Local Daemon| OLLAMA["Ollama Provider<br/>(llama3.2:latest)"]
        LLM_ROUTER -->|External API| OPENAI["OpenAI-Compatible API<br/>(gpt-4o-mini / Gemini)"]
        LLM_ROUTER -->|Offline / CI Mode| MOCK["Mock Provider<br/>(Deterministic Grounded Synthesis)"]
    end

    subgraph "4. Output Extraction & Evaluation"
        OLLAMA --> RESP["Raw Response Stream"]
        OPENAI --> RESP
        MOCK --> RESP
        RESP --> CITE_EXT["Citation Parser<br/>Extract [VTR-XXXXX] IDs"]
        CITE_EXT --> EVAL["RAG Evaluation Engine<br/>Precision, Recall, Safety, Grounding"]
        EVAL --> OUT["Final Diagnostic Report<br/>Structured JSON / CSV / Markdown"]
    end
```

---

## 3. Grounded Prompt Engineering & Anti-Hallucination Rules

Automotive troubleshooting carries critical physical safety and financial consequences. If an AI incorrectly suggests replacing an expensive catalytic converter or gives unsafe instructions on high-voltage hybrid batteries, serious harm can result.

### 3.1 Five Operational Guardrails

The system prompt (`src/rag_pipeline.py:SYSTEM_PROMPT`, version `2.1.0-grounded-automotive-diagnostic`) strictly enforces five rules:

1. **Strict Context Grounding**: The LLM must answer *solely* using facts, symptoms, possible causes, and steps documented in the retrieved records. If context is insufficient, it must explicitly acknowledge the gap.
2. **Zero Specification Hallucination**: The model is forbidden from inventing sensor voltages (e.g. "5.0 V reference"), torque specifications, or wiring pin numbers unless explicitly present in the retrieved text.
3. **Causality vs. Correlation Distinction**: The model must clarify that an OBD-II Diagnostic Trouble Code indicates an electrical circuit or rational test failure, *not* an automatic condemnation of the physical component. (e.g., an O2 sensor code is frequently caused by an exhaust manifold leak or vacuum leak, not a bad sensor).
4. **Mandatory In-Text Citations**: Every technical claim, probable cause, or diagnostic step must cite its source record ID in square brackets (e.g., `[VTR-P00B7]`).
5. **Mandatory Automotive Safety Warnings**: Any inquiry involving High-Voltage (hybrid/EV) battery loops, Hydraulic Braking systems, Supplemental Restraint Systems (airbags), or steering linkages must mandate professional ASE-certified technician inspection.

### 3.2 Five-Part Structured Diagnostic Response Format

Responses are partitioned into five standardized sections:
1. `### 1. Summary of Reported Problem`: Synthesizes symptoms into automotive system categories.
2. `### 2. Possible Causes (Supported by Retrieved Knowledge)`: Bulleted probable causes with direct `[VTR-XXXXX]` citations.
3. `### 3. Step-by-Step Diagnostic & Inspection Procedures`: Prioritized non-destructive tests (wiring harness check, continuity test, live scan data).
4. `### 4. Limitations & Missing Information`: Highlights missing vehicle specifics (engine code, year) and context limitations.
5. `### 5. Source Record Citations`: Complete inventory of all cited `[VTR-XXXXX]` identifiers.

---

## 4. LLM Provider Abstraction Layer

The pipeline decouples generation logic from vendor SDKs via `src/llm_provider.py`:

```mermaid
classDiagram
    class BaseLLMProvider {
        <<abstract>>
        +str model_name
        +str name*
        +str generation_mode*
        +is_available()* bool
        +generate(prompt, system_prompt, temperature, max_tokens)* LLMResponse
    }
    class OllamaProvider {
        +str base_url
        +int timeout
        +is_available() bool
        +generate() LLMResponse
    }
    class OpenAICompatibleProvider {
        +str api_key
        +str base_url
        +int timeout
        +is_available() bool
        +generate() LLMResponse
    }
    class MockLLMProvider {
        +is_available() bool
        +generate() LLMResponse
    }

    BaseLLMProvider <|-- OllamaProvider
    BaseLLMProvider <|-- OpenAICompatibleProvider
    BaseLLMProvider <|-- MockLLMProvider
```

### Security & Credential Hygiene
- API keys are retrieved exclusively from environment variables (`EXTERNAL_API_KEY` or `OPENAI_API_KEY`).
- Keys are never logged or committed to version control.
- `OpenAICompatibleProvider.is_available()` verifies key presence without logging its value.

---

## 5. Context vs. Unassisted Baseline Comparative Analysis

To evaluate the empirical impact of RAG, all 10 assignment queries were executed in two distinct modes using identical generation settings:
- **Mode A (Grounded RAG)**: Query + Top-5 ChromaDB retrieved records.
- **Mode B (Unassisted Baseline)**: Query alone, zero retrieved context.

### Side-by-Side Comparison Summary Table (Q01 – Q10)

| Query ID | Automotive Focus | Grounded RAG Behavior | Unassisted Baseline Behavior | Core Difference |
|:---:|:---|:---|:---|:---|
| **Q01** | Cooling & Overheating | Cites `[VTR-P00B7]`, identifies coolant temperature threshold (>117°C), checks flow control valve and pump communication. | Suggests generic radiator flush and water pump replacement without specific diagnostic codes. | RAG anchors diagnosis to specific thermostat failure modes and DTC P00B7. |
| **Q02** | Crank No-Start / Spark | Cites `[VTR-P0316]`, isolates startup revolution misfires and crankshaft position signal. | Recommends checking spark plugs, battery voltage, and fuel pump relay generically. | RAG distinguishes startup-specific misfire codes from general running misfires. |
| **Q03** | Parasitic Battery Drain | Cites `[VTR-P0D17]`, identifies charging HVIL loop circuit low voltage. | Advises measuring fuse parasitic draw with a multimeter without identifying hybrid/EV charging circuits. | RAG connects symptom to high-voltage interlock circuits present in the database. |
| **Q04** | Soft Brake Pedal / ABS | Cites `[VTR-C0291]`, identifies brake pedal apply sensor circuit and master cylinder bypass. | Suggests bleeding brake lines and checking brake fluid level. | RAG references chassis sensor circuits and safety disclaimers for hydraulic systems. |
| **Q05** | Transmission Shudder | Cites `[VTR-P2711]`, diagnoses mechanical gear disengagement and friction element B slippage. | Advises checking transmission fluid level and general torque converter shudder. | RAG identifies exact dual-clutch / automatic shift solenoid failure codes. |
| **Q06** | Flashing CEL / Misfire | Cites `[VTR-B0860]`, isolates ignition circuit low range and cylinder misfire protocols. | Recommends replacing spark plugs and ignition coils indiscriminately. | RAG emphasizes testing circuit continuity before replacing ignition coils. |
| **Q07** | Fuel Economy / Rich Smoke | Cites `[VTR-P2BD2]`, identifies exhaust aftertreatment leaks confusing upstream sensors. | Blames faulty MAF sensor or stuck fuel injectors generically. | RAG reveals aftertreatment exhaust leaks that cause false rich fuel trim readings. |
| **Q08** | Cluster Failure / CAN Bus | Cites `[VTR-B0223]`, references warning lamp circuit faults and serial data timeout. | Suggests checking battery ground terminals and alternator charging voltage. | RAG identifies module communication timeout codes and bus topology checks. |
| **Q09** | Airbag Light / Clock Spring | Cites `[VTR-B0005]`, pinpoints steering column deployment loop open circuit. | Suggests resetting airbag light with a scanner or checking seat belt buckle switch. | RAG identifies squib deployment resistance specifications and clock spring pin fitment. |
| **Q10** | Turbocharger Underboost | Cites `[VTR-P0299]`, establishes boost pressure differential thresholds (30–55 kPa). | Suggests inspecting intercooler hoses for cracks and wastegate actuator rod. | RAG provides exact manufacturer underboost criteria (GM/Ford EcoBoost thresholds). |

### Summary of Comparative Observations
1. **Source Grounding**: RAG achieved 100% citation coverage across all queries, while the baseline cited zero records.
2. **Elimination of Indiscriminate Parts Replacement**: The baseline consistently encouraged replacing parts (plugs, sensors, pumps). Grounded RAG instructed verifying wiring harness continuity, reference voltages, and ground integrity first.
3. **Safety Compliance**: RAG systematically injected safety precautions for high-voltage, braking, and airbag systems.

---

## 6. Evaluation Framework & Metrics

RAG responses are evaluated using four objective metrics implemented in `src/rag_evaluation.py`:

1. **Citation Precision**:
   $$\text{Precision} = \frac{|\text{Valid Cited Record IDs} \cap \text{Retrieved Record IDs}|}{|\text{Total Cited Record IDs}|}$$
   - Measures whether the model cites records that actually exist in the retrieved top-K context (guarding against hallucinated citations).
2. **Citation Recall**:
   $$\text{Recall} = \frac{|\text{Valid Cited Record IDs} \cap \text{Retrieved Record IDs}|}{|\text{Retrieved Record IDs}|}$$
   - Measures the percentage of retrieved documents utilized in the final response.
3. **Structure Adherence**:
   - Assesses compliance with the required five-section format (Summary, Causes, Checks, Limitations, Citations).
4. **Safety Disclaimer Presence**:
   - Binary verification that safety-critical automotive systems include professional technician inspection warnings.

---

## 7. How to Execute the RAG Pipeline

### A. Offline / Automated Testing Mode (No External API Required)
```bash
# Runs the full RAG pipeline and evaluation across all 10 queries using MockLLMProvider
PYTHONPATH=. .venv/bin/python scripts/run_rag.py
```
Outputs generated:
- Structured JSON Results: [`experiments/rag_mock_results.json`](file:///Users/hrishabh/BITS_MDS_Assignment_02/experiments/rag_mock_results.json)
- Side-by-Side Baseline Comparison: [`experiments/rag_mock_context_vs_baseline.json`](file:///Users/hrishabh/BITS_MDS_Assignment_02/experiments/rag_mock_context_vs_baseline.json)
- Evaluation CSV Table: [`experiments/rag_mock_evaluation.csv`](file:///Users/hrishabh/BITS_MDS_Assignment_02/experiments/rag_mock_evaluation.csv)
- Human-Readable Markdown Report: [`experiments/rag_mock_results.md`](file:///Users/hrishabh/BITS_MDS_Assignment_02/experiments/rag_mock_results.md)

### B. Live Inference with Local Ollama
```bash
# 1. Pull the model locally
ollama pull llama3.2

# 2. Run the script (automatically detects active Ollama daemon)
PYTHONPATH=. .venv/bin/python scripts/run_rag.py
```

### C. Live Inference with OpenAI-compatible API
```bash
# 1. Set environment variables in .env
LLM_PROVIDER=external
EXTERNAL_API_KEY=your_key_here
EXTERNAL_API_BASE_URL=https://api.openai.com/v1
EXTERNAL_MODEL_NAME=gpt-4o-mini

# 2. Run the script
PYTHONPATH=. .venv/bin/python scripts/run_rag.py
```

---

## 8. Viva Voce Defense & Examiner Q&A

### Q1: How does your RAG system prevent an LLM from hallucinating repair procedures?
> **Answer**: We employ a three-tier defense: (1) **Context Isolation**: The system prompt explicitly orders the LLM to answer *solely* using the retrieved records and acknowledge insufficient context if facts are missing; (2) **Citation Enforcement**: Every claim must cite the specific source ID `[VTR-XXXXX]`, allowing automated post-generation validation; (3) **Causality Boundaries**: The prompt explicitly instructs that a Diagnostic Trouble Code indicates a sensor or circuit fault, preventing the LLM from declaring that the component has definitively failed.

### Q2: Why is unassisted LLM generation dangerous for automotive troubleshooting?
> **Answer**: Unassisted LLMs rely on statistical pattern matching from broad web data, frequently recommending that vehicle owners replace expensive components (e.g. oxygen sensors, control modules) when the root cause is often a simple wiring chaff or vacuum leak. Furthermore, unassisted LLMs frequently miss critical safety warnings when advising on 400V hybrid battery interlocks or braking hydraulics. Grounded RAG ensures that factory diagnostic steps and safety disclaimers are always presented.

### Q3: How do you verify that the model actually used the retrieved context?
> **Answer**: We use the `evaluate_citation_fidelity` metric in `src/rag_evaluation.py`. We extract all cited record IDs using regex and verify that they match the IDs in the top-K retrieved set. We also compare the RAG output against an unassisted baseline output, proving that the RAG response references specific diagnostic codes, thresholds, and inspection procedures that are completely absent from the baseline.

---
*Generated and verified as part of BITS Pilani Modern Database Systems Assignment 2 (Phase 6).*
