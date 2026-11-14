# Comprehensive Experimental Results & Comparative Evaluation

**Course:** BITS Pilani WILP – Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Group:** 20  
**Team Members:**
- Priya N (BITS ID: 2026NS12087) — 20% Contribution
- Mohamed Ibrahim M (BITS ID: 2026NS12021) — 20% Contribution
- Hrishabh Gupta (BITS ID: 2026NS12122) — 20% Contribution
- Aditya Singhal (BITS ID: 2026NS12028) — 20% Contribution
- Rupesh Kumar Singh (BITS ID: 2026NS12128) — 20% Contribution

---

## 1. Overview of Experimental Framework

To evaluate the system thoroughly, three major empirical experiments were designed, executed, and archived:
1. **Phase 4: Semantic Search Evaluation:** Top-K retrieval evaluation ($K=3, 5, 10$) across 10 diverse automotive symptom queries against the 9,532-record ChromaDB database.
2. **Phase 5: Vector Distance Metric Comparison:** Exhaustive comparison of Cosine Similarity, Euclidean Distance ($L_2$), and Dot Product across all 9,532 records using vectorized NumPy (60 distinct query-metric-K configurations).
3. **Phase 6 & 6.1: RAG vs No-Context Baseline Evaluation:** Side-by-side evaluation of grounded RAG responses versus parametric baseline LLM responses using both local Meta Llama 3.2 (3.2B parameters) and offline deterministic synthesis.

All raw results, JSON logs, CSV tables, and Markdown reports are permanently preserved in the `experiments/` directory.

---

## 2. Phase 4: Semantic Search & Top-K Retrieval Results

Ten standardized queries (Q01–Q10) representing common and critical automotive fault scenarios were evaluated across $K \in \{3, 5, 10\}$:

| Query ID | Automotive Symptom / Fault Narrative | Top-1 Retrieved DTC | System Domain | Mean Distance ($K=5$) |
|---|---|---|---|---|
| **Q01** | Engine misfire under heavy acceleration | P0300 (Random Misfire) | Engine | 0.284 |
| **Q02** | Brake pedal feels spongy and sinks to floor | C0040 (Brake Pedal Switch) | Brakes | 0.312 |
| **Q03** | Battery drain overnight when vehicle parked | P0A1F / P0562 (Charging) | Electrical | 0.389 |
| **Q04** | Air conditioning blowing warm air at idle | P0530 (A/C Refrigerant) | Body/Climate | 0.341 |
| **Q05** | Transmission slipping between 2nd and 3rd | P0730 (Incorrect Gear Ratio) | Transmission | 0.298 |
| **Q06** | Engine overheating in stop-and-go traffic | P00B7 (Engine Coolant Flow) | Engine/Cooling | 0.305 |
| **Q07** | Steering wheel vibrating at highway speeds | C0051 (Steering Wheel Angle) | Suspension/Steering | 0.362 |
| **Q08** | Strong fuel smell inside vehicle cabin | P0440 (EVAP System Malfunction) | Emissions | 0.318 |
| **Q09** | Airbag warning light illuminated on dashboard | B0001 (Driver Airbag Squib) | Restraints / SRS | 0.354 |
| **Q10** | High-voltage hybrid system warning light | P0A80 (Replace Hybrid Battery) | Hybrid / EV Drive | 0.267 |

### 2.1 Retrieval Findings
- **Semantic Mapping:** The dense vector index mapped driver-reported natural language descriptions (e.g., "spongy pedal", "strong fuel smell") to exact engineering fault codes (C0040, P0440) without requiring the user to know the diagnostic code.
- **Top-K Trade-off:** $K=5$ proved optimal for RAG context framing: it supplied sufficient procedural breadth (4–5 candidate root causes) while keeping context length under 1,500 tokens, well within the LLM's attention window.

---

## 3. Phase 5: Mathematical Similarity Metrics Evaluation

Every query was evaluated using pure vectorized NumPy against all 9,532 records across three metrics:
1. **Cosine Similarity** ($\cos(\mathbf{x}, \mathbf{q})$)
2. **Euclidean Distance** ($\|\mathbf{x} - \mathbf{q}\|_2$)
3. **Dot Product** ($\mathbf{x} \cdot \mathbf{q}$)

### 3.1 Quantitative Metric Comparison (Q01 Example, $K=5$)

| Rank | Document ID | Title | Cosine Similarity | Euclidean Distance ($L_2$) | Dot Product |
|---|---|---|---|---|---|
| **1** | `VTR-P0300` | DTC P0300 - Random/Multiple Misfire | **0.7812** | **0.6615** | **0.7812** |
| **2** | `VTR-P0301` | DTC P0301 - Cylinder 1 Misfire Detected | **0.7548** | **0.7003** | **0.7548** |
| **3** | `VTR-P0302` | DTC P0302 - Cylinder 2 Misfire Detected | **0.7491** | **0.7084** | **0.7491** |
| **4** | `VTR-P0303` | DTC P0303 - Cylinder 3 Misfire Detected | **0.7435** | **0.7162** | **0.7435** |
| **5** | `VTR-P0304` | DTC P0304 - Cylinder 4 Misfire Detected | **0.7388** | **0.7228** | **0.7388** |

### 3.2 Rank Correlation Analysis
Across all 60 evaluations ($10\text{ queries} \times 3\text{ metrics} \times 2\text{ values of }K$):
- **Spearman Rank Correlation ($\rho$):** **1.0000** (identical rankings across all 60 configurations)
- **Kendall's Tau ($\tau$):** **1.0000**
- **Conclusion:** Because vectors are unit normalized ($\|\mathbf{x}\| = 1$), Euclidean distance, Cosine similarity, and Dot Product are mathematically equivalent in ranking order.

---

## 4. Phase 6 & 6.1: RAG vs No-Context Baseline Evaluation

To evaluate whether RAG delivers substantive value over an ungrounded LLM, all 10 assignment queries were executed under two conditions:
1. **RAG Mode:** LLM is provided top-5 retrieved diagnostic records with explicit schema fields (symptoms, causes, steps, codes).
2. **No-Context Baseline Mode:** LLM is provided only the driver symptom query without any database records.

### 4.1 Real LLM (Ollama Llama 3.2 3B) Benchmark Metrics

| Evaluation Metric | No-Context Baseline | Grounded RAG Pipeline | Impact / Delta |
|---|---|---|---|
| **Average Citation Precision** | 0.0% (0 citations) | **100.0%** (All citations match retrieved IDs) | $+100.0\%$ |
| **Hallucination Rate** | High (invented specs, generic guesses) | **0.0%** (Strictly bounded to context) | $-100.0\%$ |
| **Domain Specificity** | Broad generalities ("take to a shop") | **Specific Diagnostic Steps & Pins** | Transformative |
| **Average Response Length** | 312 words | 487 words | $+56.1\%$ detail |
| **Safety Warning Adherence** | 40% (Inconsistent) | **100.0%** (Mandatory warning banners) | $+60.0\%$ |
| **Mean Inference Latency** | 98.4 seconds | 118.2 seconds | $+19.8\text{ s}$ (Context processing) |

### 4.2 Negative Findings & Retrieval Boundary Cases
The evaluation deliberately analyzed where the system reached its design boundaries:
1. **Q03 (ICE 12V Parasitic Drain):** The generic OBD-II standard primarily indexes electrical DTCs relating to charging circuit low voltage (`P0562`) or hybrid DC-DC converters (`P0A1F`). Parasitic 12V standby draw (e.g., sticking glovebox relay) typically does not set a DTC. The RAG pipeline correctly warned that parasitic draw requires physical milliammeter fuse-pull testing rather than relying solely on scanner codes.
2. **Q09 (SRS Airbag Warning):** The RAG pipeline successfully retrieved driver airbag squib circuit codes (`B0001`), but the safety guardrails intervened to prohibit ohmmeter continuity probing across airbag detonator squibs, preventing accidental pyrotechnic deployment.
