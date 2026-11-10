# Phase 4 vs. Phase 5 Retrieval Reconciliation & Verification Report

**Project Title**: Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Academic Module**: BITS Pilani WILP — Modern Database Systems (Assignment 2)  
**Verification Date**: November 2026  
**Investigated Commits**:
- Phase 4: `c1e7ad5c69373442642d3703ae6a7e10e953ec61`
- Phase 5: `475a9d40d3405a8764378bc2923799b0e7579cea`
**Dataset**: 9,532 authentic vehicle diagnostic records (`data/processed/vehicle_troubleshooting.json`)  
**Persistent Collection**: `vehicle_troubleshooting_kb` (9,532 records in `database/chroma_db`)  

---

## 1. Executive Summary & Core Finding

An intensive investigation was conducted to determine why previous summary narratives appeared to report conflicting Top-1 retrieval results between Phase 4 and Phase 5.

### Primary Root Cause
1. **The underlying machine-generated JSON result artifacts are 100% IDENTICAL**:
   The actual raw search results produced in Phase 4 (`experiments/semantic_search_results.json`, committed in `c1e7ad5`) and Phase 5 (`experiments/similarity_comparison_results.json`, committed in `475a9d4`) produced **the exact same Top-1 document for all 10 queries without exception**.
2. **The perceived discrepancy was caused by documentation narrative confusion**:
   In Phase 4, the documentation file `docs/semantic_search_experiments.md` contained manual illustrative narratives and tables that conflated:
   - **Theoretical Query Design Targets** (e.g., target diagnostic codes listed during query ideation such as `P0300`, `P2534`).
   - **Compound Metadata Filtered Results** (e.g., Filter F03 restricting to `network_and_communication` which retrieved `VTR-U0039` as #1; Filter F04 restricting to `electrical_and_body` which retrieved `VTR-B0001` as #1; Filter F05 retrieving `VTR-P20CF` as #1).
   - **Unfiltered Semantic Search Results** (where `VTR-B0223`, `VTR-B0005`, and `VTR-P2BD2` were the actual mathematical #1 ranks).
3. **No Code, Embedding, or Dataset Regression Occurred**:
   Phase 5 did not modify the dataset, embedding models, vector dimensions, or normalization procedures. All 9,532 records remain intact, unit-normalized, and identical.

---

## 2. Step 1: Git Inspection & File Audit

A git audit of Phase 4 (`c1e7ad5`) versus Phase 5 (`475a9d4`) confirmed:

| Component | Status in Phase 4 | Status in Phase 5 | Change Detected |
|:---|:---:|:---:|:---:|
| **Dataset Content** (`vehicle_troubleshooting.json`) | 9,532 records | 9,532 records | **None** (identical file, 0 bytes diff) |
| **Document Construction** (`src/embeddings.py:create_record_text`) | Standard schema format | Standard schema format | **None** (unmodified) |
| **Embedding Model** | `all-MiniLM-L6-v2` | `all-MiniLM-L6-v2` | **None** (identical model) |
| **Vector Normalization** | `normalize_embeddings=True` | `normalize_embeddings=True` | **None** (unit norm $\|\mathbf{x}\|_2 = 1.0$) |
| **ChromaDB Collection** | 9,532 records | 9,532 records | **None** (read-only verification) |
| **Query Definitions** (`assignment_queries.json`) | 10 defined queries | 10 defined queries | **None** (unmodified) |

---

## 3. Step 2: Query Text Verification (Q01 – Q10)

We programmatically compared the query strings from `data/queries/assignment_queries.json`, `experiments/semantic_search_results.json` (Phase 4), and `experiments/similarity_comparison_results.json` (Phase 5).

| Query ID | Definition Text == Phase 4? | Definition Text == Phase 5? | Phase 4 == Phase 5? | Full Verbatim Query Text |
|:---:|:---:|:---:|:---:|:---|
| **Q01** | **True** | **True** | **True** | *Engine overheating rapidly at highway speeds with boiling coolant in reservoir and radiator fan not engaging* |
| **Q02** | **True** | **True** | **True** | *Engine cranks strongly but fails to start with smell of unburnt fuel and no spark on ignition coils* |
| **Q03** | **True** | **True** | **True** | *Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle* |
| **Q04** | **True** | **True** | **True** | *Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard* |
| **Q05** | **True** | **True** | **True** | *Automatic transmission delayed engagement into drive and harsh shuddering when shifting between second and third gears* |
| **Q06** | **True** | **True** | **True** | *Check engine light flashing with rough idling, severe loss of engine power, and heavy vehicle vibration under load* |
| **Q07** | **True** | **True** | **True** | *Drastic drop in fuel economy with black smoke from exhaust and rich fuel mixture odor during acceleration* |
| **Q08** | **True** | **True** | **True** | *Instrument cluster displays multiple failure lamps with total loss of CAN communication between engine and transmission control modules* |
| **Q09** | **True** | **True** | **True** | *Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring* |
| **Q10** | **True** | **True** | **True** | *Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills* |

**Finding**: There is zero difference in whitespace, punctuation, casing, or wording across all queries between Phase 4 and Phase 5.

---

## 4. Step 3: Document Embedding Vectors & Cryptographic Fingerprints

To verify that the underlying embedding vectors did not change between phases, representative records cited across both phases were extracted from the persistent ChromaDB collection and verified against the processed dataset:

| Record ID | Dimension | $L_2$ Norm | SHA-256 Fingerprint (First 16 hex) | First 5 Vector Components | Text Matches `create_record_text`? |
|:---|:---:|:---:|:---:|:---|:---:|
| `VTR-P00B7` | 384 | 1.000000 | `da7f5e40e4a7fc18` | `[-0.04648, -0.04913, -0.05535, 0.07374, -0.0018]` | **True** |
| `VTR-P0316` | 384 | 1.000000 | `8aae590a9afec6fe` | `[-0.08780, -0.04204, -0.03024, 0.03788, 0.00349]` | **True** |
| `VTR-P2534` | 384 | 1.000000 | `e39fec93b14e370b` | `[-0.04480, -0.04710, 0.02001, 0.01284, 0.03011]` | **True** |
| `VTR-P0D17` | 384 | 1.000000 | `54b0891c6d0d96ff` | `[-0.11314, 0.06308, -0.03667, -0.01144, 0.09736]` | **True** |
| `VTR-C0619` | 384 | 1.000000 | `8abb3eb25abd3cd3` | `[-0.08449, -0.08932, 0.00462, -0.05266, -0.05289]` | **True** |
| `VTR-C0291` | 384 | 1.000000 | `849b35945c39eb2e` | `[-0.07369, -0.10163, 0.02361, -0.03860, 0.00710]` | **True** |
| `VTR-P0732` | 384 | 1.000000 | `997c8605b79faf8f` | `[-0.12961, -0.10670, 0.00877, 0.10188, 0.04418]` | **True** |
| `VTR-P2711` | 384 | 1.000000 | `cdecc423cb48af8e` | `[-0.09070, -0.05594, 0.04501, 0.08685, -0.02940]` | **True** |
| `VTR-P0300` | 384 | 1.000000 | `5703c8a18063a4e5` | `[-0.07986, -0.03091, -0.04796, 0.01567, 0.04488]` | **True** |
| `VTR-B0860` | 384 | 1.000000 | `2cae6fc380e6f5a2` | `[-0.06113, -0.01309, 0.07047, -0.04544, -0.04899]` | **True** |
| `VTR-U0039` | 384 | 1.000000 | `8bac95c5f4f105b4` | `[-0.05097, -0.05397, -0.00715, -0.00931, 0.06573]` | **True** |
| `VTR-B0223` | 384 | 1.000000 | `59a7db34396cfebf` | `[-0.02211, -0.03279, -0.04376, 0.03667, 0.04114]` | **True** |
| `VTR-P20CF` | 384 | 1.000000 | `c4e17af402ea1c5e` | `[-0.06169, -0.01383, 0.00968, 0.02639, 0.05874]` | **True** |
| `VTR-P2BD2` | 384 | 1.000000 | `80ceac80cb1d8d0c` | `[-0.05280, -0.01067, 0.08024, 0.01109, 0.11517]` | **True** |
| `VTR-B0001` | 384 | 1.000000 | `cbd3c7cbd47e2dfe` | `[-0.02891, -0.00889, -0.05383, 0.01601, 0.03700]` | **True** |
| `VTR-B0005` | 384 | 1.000000 | `23d296dcce042ae0` | `[-0.06581, -0.02534, -0.07436, 0.02830, 0.06496]` | **True** |
| `VTR-P0299` | 384 | 1.000000 | `9a7ac370f991a2d2` | `[-0.13754, -0.02815, -0.01942, 0.06269, 0.09632]` | **True** |

**Finding**: All vectors are unit-normalized ($L_2 = 1.000000$), contain 384 dimensions, and correspond exactly to the text generated by `create_record_text`.

---

## 5. Step 4: Mathematical Equivalence on Unit-Normalized Vectors

Using the verified 9,532 document embeddings and 10 query embeddings, we verified the exact mathematical identities:

1. **Cosine vs. Dot Product**:
   $$\max_{i} |\cos(\mathbf{x}_i, \mathbf{q}) - (\mathbf{x}_i \cdot \mathbf{q})| \le 5.96 \times 10^{-8}$$
   Identical within 32-bit floating point precision.
2. **Euclidean Distance vs. Cosine Formula**:
   $$\max_{i} |d_{L_2}(\mathbf{x}_i, \mathbf{q}) - \sqrt{2(1 - \cos(\mathbf{x}_i, \mathbf{q}))}| \le 2.34 \times 10^{-7}$$
   Strictly verified across all 95,320 vector distance pairs ($10 \times 9,532$).
3. **Rank Agreement**:
   - Top-1 match across all 3 metrics: **10/10 queries (100%)**
   - Top-5 match across all 3 metrics: **10/10 queries (100%)**
   - Top-10 match across all 3 metrics: **10/10 queries (100%)**

---

## 6. Step 5: Discrepancy Investigation & Resolution Table

Below is the exhaustive reconciliation of every discrepancy listed in the review request, comparing the perceived Phase 4 report value, the actual Phase 4 JSON output, and the Phase 5 exhaustive NumPy output:

| Query ID | Perceived Phase 4 Value | Actual Phase 4 Top-1 (`experiments/semantic_search_results.json`) | Phase 5 Top-1 (`experiments/similarity_comparison_results.json`) | Exact Match? | True Source of Perceived Value |
|:---:|:---:|:---:|:---:|:---:|:---|
| **Q01** | `VTR-P00B7` | `VTR-P00B7` (dist: 0.6039) | `VTR-P00B7` (cos: 0.3961) | **MATCH** | Consistent across all files. |
| **Q02** | `VTR-P0316` | `VTR-P0316` (dist: 0.6113) | `VTR-P0316` (cos: 0.3887) | **MATCH** | Consistent across all files. |
| **Q03** | `VTR-P2534` | `VTR-P0D17` (dist: 0.5376) | `VTR-P0D17` (cos: 0.4624) | **MATCH** | `P2534` was an automotive ignition switch code from initial query planning notes. The actual ChromaDB query retrieved `VTR-P0D17` (HVIL battery low circuit). |
| **Q04** | `VTR-C0619` | `VTR-C0291` (dist: 0.4759) | `VTR-C0291` (cos: 0.5241) | **MATCH** | `docs/semantic_search_experiments.md` (line 72) mistakenly highlighted `VTR-C0619` (rank 15, dist 0.5381) as narrative text, but the JSON output has always had `VTR-C0291` at rank 1. |
| **Q05** | `VTR-P0732` | `VTR-P2711` (dist: 0.5015) | `VTR-P2711` (cos: 0.4985) | **MATCH** | `P0732` (Gear 2 incorrect ratio) was a hypothesized target fault. Actual ChromaDB and NumPy search retrieved `VTR-P2711` (Unexpected Mechanical Gear Disengagement). |
| **Q06** | `VTR-P0300` | `VTR-B0860` (dist: 0.5494) | `VTR-B0860` (cos: 0.4506) | **MATCH** | `P0300` (Random/Multiple Cylinder Misfire) was the textbook code listed in the query design table. Both Phase 4 and Phase 5 retrieved `VTR-B0860`. |
| **Q07** | `VTR-P20CF` | `VTR-P2BD2` (dist: 0.6449) | `VTR-P2BD2` (cos: 0.3551) | **MATCH** | `VTR-P20CF` was the Top-1 match for **Filter F05** (`engine_and_transmission` + `medium` severity). For unfiltered Q07, both Phase 4 and Phase 5 retrieved `VTR-P2BD2`. |
| **Q08** | `VTR-U0039` | `VTR-B0223` (dist: 0.4971) | `VTR-B0223` (cos: 0.5029) | **MATCH** | `VTR-U0039` was the Top-1 match for **Filter F03** (`network_and_communication` + `high` severity). For unfiltered Q08, both Phase 4 and Phase 5 retrieved `VTR-B0223` (`VTR-U0039` is Rank 3). |
| **Q09** | `VTR-B0001` | `VTR-B0005` (dist: 0.4656) | `VTR-B0005` (cos: 0.5344) | **MATCH** | `VTR-B0001` was the Top-1 match for **Filter F04** (`electrical_and_body` + `high` severity). For unfiltered Q09, both Phase 4 and Phase 5 retrieved `VTR-B0005` (`VTR-B0001` is Rank 3). |
| **Q10** | `VTR-P0299` | `VTR-P0299` (dist: 0.4707) | `VTR-P0299` (cos: 0.5293) | **MATCH** | Consistent across all files. |

---

## 7. Step 6: Exhaustive Coverage Verification

We verified that the similarity computations in Phase 5 performed a true, exhaustive evaluation:
- **Total Unique Records in Database**: Exactly **9,532**.
- **Matrix Dimension in NumPy Memory**: **$(9532, 384)$** of `float32`.
- **Query Vector Dimension**: **$384$** of `float32`.
- **Records Evaluated Per Query**: Exactly **9,532**.
- **Zero Dummy/Random Vectors**: All 9,532 vectors originate from real diagnostic records stored in ChromaDB.
- **Top-5 and Top-10 Selection**: Derived by sorting the entire array of 9,532 distance/similarity values.

---

## 8. Step 7: Automated Test Suite

Running the full pytest suite:
```bash
PYTHONPATH=. .venv/bin/pytest tests/ -v
```
Output:
```
======================= 39 passed, 5 warnings in 14.12s ========================
```
- 10/10 dataset tests passed.
- 8/8 ChromaDB manager & persistence tests passed.
- 11/11 semantic search and metadata filter tests passed.
- 10/10 NumPy similarity and mathematical equivalence tests passed.
- ChromaDB collection record count verified at exactly **9,532** before and after all test executions.

---

## 9. Conclusion

The apparent discrepancies between Phase 4 and Phase 5 were strictly **documentation narrative artifacts** where metadata filter winners and query design target codes were mistakenly cited in narrative text. The actual database vectors, query strings, and retrieval outputs have been verified to be in **100% agreement**.
