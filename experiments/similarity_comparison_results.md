# Phase 5: Exhaustive NumPy Similarity Metrics Comparison Report

## Modern Database Systems (Assignment 2) — Academic Evaluation

- **Execution Timestamp**: `2026-11-08T09:39:03.601961+00:00`
- **Dataset Size**: `9,532` authentic diagnostic records
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: `384`
- **Vector Normalization**: Document Embeddings = `||x||_2 = 1.0` (`True`), Query Embeddings = `||q||_2 = 1.0`
- **Metrics Evaluated**: Euclidean Distance ($L_2$), Cosine Similarity, Dot Product
- **Configurations Evaluated**: 10 Queries $\times$ 3 Metrics $\times$ 2 Cutoffs ($K=5, K=10$) = **60 evaluations**

---

## 1. Mathematical Foundations & Metric Formulations

For a query vector $\mathbf{q} \in \mathbb{R}^D$ and document vector $\mathbf{x}_i \in \mathbb{R}^D$:

### A. Euclidean Distance ($L_2$ Norm)
$$\text{dist}_{L_2}(\mathbf{x}_i, \mathbf{q}) = \|\mathbf{x}_i - \mathbf{q}\|_2 = \sqrt{\sum_{j=1}^D (x_{i,j} - q_j)^2}$$
- **Direction**: Ascending sort (smaller distance denotes higher semantic proximity).
- **Geometric Property**: Measures absolute geometric distance in Euclidean hyperspace.

### B. Cosine Similarity
$$\cos(\mathbf{x}_i, \mathbf{q}) = \frac{\mathbf{x}_i \cdot \mathbf{q}}{\|\mathbf{x}_i\|_2 \|\mathbf{q}\|_2} = \frac{\sum_{j=1}^D x_{i,j} q_j}{\sqrt{\sum_{j=1}^D x_{i,j}^2} \sqrt{\sum_{j=1}^D q_j^2}}$$
- **Direction**: Descending sort (higher score denotes closer angular alignment).
- **Range**: $[-1.0, 1.0]$.

### C. Dot Product (Inner Product)
$$\mathbf{x}_i \cdot \mathbf{q} = \sum_{j=1}^D x_{i,j} q_j$$
- **Direction**: Descending sort (higher value denotes higher inner product).
- **Magnitude Sensitivity**: Scales directly with the magnitudes $\|\mathbf{x}_i\|_2$ and $\|\mathbf{q}\|_2$.

---

## 2. Impact of Vector Normalization ($L_2$ Unit Norms)

When vector embeddings are normalized such that $\|\mathbf{x}_i\|_2 = 1.0$ and $\|\mathbf{q}\|_2 = 1.0$:

1. **Identity of Cosine Similarity and Dot Product**:
   $$\cos(\mathbf{x}_i, \mathbf{q}) = \frac{\mathbf{x}_i \cdot \mathbf{q}}{1.0 \times 1.0} = \mathbf{x}_i \cdot \mathbf{q}$$
   Cosine similarity and Dot Product yield numerically identical scores and identical rankings.

2. **Strict Monotonic Equivalence with Euclidean Distance**:
   $$\|\mathbf{x}_i - \mathbf{q}\|_2^2 = \|\mathbf{x}_i\|_2^2 + \|\mathbf{q}\|_2^2 - 2 (\mathbf{x}_i \cdot \mathbf{q}) = 1 + 1 - 2 \cos(\mathbf{x}_i, \mathbf{q}) = 2(1 - \cos(\mathbf{x}_i, \mathbf{q}))$$
   $$\text{dist}_{L_2}(\mathbf{x}_i, \mathbf{q}) = \sqrt{2(1 - \cos(\mathbf{x}_i, \mathbf{q}))}$$
   Because $\sqrt{2(1 - s)}$ is a strictly monotonically decreasing function of $s = \cos(\mathbf{x}_i, \mathbf{q})$ on $[-1, 1]$, sort order is preserved identically: sorting in ascending order of Euclidean distance yields the exact same permutation as sorting in descending order of Cosine similarity.

---

## 3. Synthetic Metric Divergence Experiment (Unnormalized Vectors)

To illustrate the divergence of metrics when vector lengths vary, a controlled synthetic experiment was executed:
- **Query $\mathbf{q}$**: `[1.0, 0.0]` (unit vector along x-axis)
- **Doc A (collinear, unit)**: `[1.0, 0.0]` (norm = 1.0, angle = 0°)
- **Doc B (collinear, huge)**: `[10.0, 0.0]` (norm = 10.0, angle = 0°)
- **Doc C (small, angled)**: `[0.9, 0.2]` (norm = 0.92, angle = 12.5°)
- **Doc D (huge, orthogonal)**: `[0.0, 10.0]` (norm = 10.0, angle = 90°)

### Unnormalized Rankings Comparison Table
| Document | Euclidean Rank (Score) | Cosine Rank (Score) | Dot Product Rank (Score) |
|:---|:---:|:---:|:---:|
| **Doc_A (unit, collinear)** | #1 (0.0000) | #1 (1.0000) | #2 (1.0000) |
| **Doc_B (huge, collinear)** | #3 (9.0000) | #2 (1.0000) | #1 (10.0000) |
| **Doc_C (small, angled)** | #2 (0.2236) | #3 (0.9762) | #3 (0.9000) |
| **Doc_D (huge, orthogonal)** | #4 (10.0499) | #4 (0.0000) | #4 (0.0000) |

> [!IMPORTANT]
> **Key Analytical Observation**:
> On unnormalized vectors, Dot Product ranks Doc B #1 with an overwhelming score of 10.0 purely due to its magnitude, even though Doc A is identical in orientation. Euclidean distance ranks Doc A #1 (distance 0.0) but pushes Doc B down to #3 (distance 9.0) because of length disparity. Cosine similarity correctly isolates orientation, ranking both Doc A and Doc B equally at 1.000. Once normalized, all three metrics produce identical rank order.

---

## 4. Empirical Performance & Computation Latency

Full exhaustive matrix search across all 9,532 records (384 dimensions) on CPU:

| Metric | Mean Latency (ms) | Min Latency (ms) | Max Latency (ms) | Std Dev (ms) |
|:---|:---:|:---:|:---:|:---:|
| **Dot Product** | `0.25` ms | `0.22` ms | `0.36` ms | `0.04` ms |
| **Cosine Similarity** | `2.14` ms | `2.01` ms | `2.51` ms | `0.15` ms |
| **Euclidean Distance** | `3.44` ms | `2.68` ms | `7.65` ms | `1.44` ms |

- **Dot Product** is fastest because it executes as a single optimized BLAS matrix-vector product (`GEMV`).
- **Cosine Similarity** requires additional norm calculations and floating-point divisions.
- **Euclidean Distance** requires broadcasting subtraction, squaring, summation, and elementwise square roots across $9532 \times 384$ entries.

---

## 5. Exhaustive Query Retrieval Results (Q01 – Q10)

### Query Q01: Engine Cooling & Thermal Management
- **Query Text**: *"Engine overheating rapidly at highway speeds with boiling coolant in reservoir and radiator fan not engaging"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `7.647 ms` | Cosine: `2.513 ms` | Dot: `0.244 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P00B7` | `0.3961` | `0.3961` | `1.0990` | DTC P00B7 - Engine Coolant Flow Low/Performance | `P00B7` | engine_and_transmission |
| 2 | `VTR-P2B61` | `0.3491` | `0.3491` | `1.1410` | DTC P2B61 - Engine Coolant Flow Control Valve Stuck Closed | `P2B61` | engine_and_transmission |
| 3 | `VTR-U0698` | `0.3384` | `0.3384` | `1.1503` | DTC U0698 - Lost Communication With Coolant Pump E | `U0698` | network_and_communication |
| 4 | `VTR-P2D8A` | `0.3313` | `0.3313` | `1.1564` | DTC P2D8A - Fan 2 Control Module Over Temperature | `P2D8A` | engine_and_transmission |
| 5 | `VTR-P26CB` | `0.3277` | `0.3277` | `1.1595` | DTC P26CB - Engine Coolant Pump Performance/Stuck Off | `P26CB` | engine_and_transmission |

### Query Q02: Ignition & Starting System Malfunction
- **Query Text**: *"Engine cranks strongly but fails to start with smell of unburnt fuel and no spark on ignition coils"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `3.231 ms` | Cosine: `2.081 ms` | Dot: `0.36 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P0316` | `0.3887` | `0.3887` | `1.1057` | DTC P0316 - Engine Misfire Detected on Startup (First 1000 Revolutions) | `P0316` | engine_and_transmission |
| 2 | `VTR-P2314` | `0.3817` | `0.3817` | `1.1121` | DTC P2314 - Ignition Coil E Secondary Circuit | `P2314` | engine_and_transmission |
| 3 | `VTR-P2E5C` | `0.3766` | `0.3766` | `1.1166` | DTC P2E5C - Cylinder 4 Alternative Fuel Misfire Detected | `P2E5C` | engine_and_transmission |
| 4 | `VTR-P2E5E` | `0.3629` | `0.3629` | `1.1288` | DTC P2E5E - Cylinder 6 Alternative Fuel Misfire Detected | `P2E5E` | engine_and_transmission |
| 5 | `VTR-P2A2F` | `0.3627` | `0.3627` | `1.1290` | DTC P2A2F - Alternative Fuel Tank Shutoff Valve E Control Circuit Performance/Stuck Off | `P2A2F` | engine_and_transmission |

### Query Q03: Parasitic Battery Drain & Body Electrical
- **Query Text**: *"Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle"*
- **Subsystem**: `electrical_and_body`
- **Latencies**: Euclidean: `2.943 ms` | Cosine: `2.033 ms` | Dot: `0.236 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `0.8182`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P0D17` | `0.4624` | `0.4624` | `1.0369` | DTC P0D17 - Battery Charging System A High Voltage Interlock Circuit Low | `P0D17` | engine_and_transmission |
| 2 | `VTR-P0B57` | `0.4310` | `0.4310` | `1.0668` | DTC P0B57 - Hybrid/EV Battery Voltage Sense F Circuit High | `P0B57` | engine_and_transmission |
| 3 | `VTR-P0D46` | `0.4288` | `0.4288` | `1.0688` | DTC P0D46 - Battery Charger 14 Volt Output Voltage Sensor Circuit Intermittent/Erratic | `P0D46` | engine_and_transmission |
| 4 | `VTR-P0D47` | `0.4265` | `0.4265` | `1.0709` | DTC P0D47 - Battery Charger 14 Volt Output Current Sensor Circuit | `P0D47` | engine_and_transmission |
| 5 | `VTR-P0D23` | `0.4243` | `0.4243` | `1.0731` | DTC P0D23 - Battery Charger A Output Shorted | `P0D23` | engine_and_transmission |

### Query Q04: Braking Hydraulics & Anti-Lock Braking System
- **Query Text**: *"Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard"*
- **Subsystem**: `brakes_and_suspension`
- **Latencies**: Euclidean: `3.885 ms` | Cosine: `2.308 ms` | Dot: `0.244 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-C0291` | `0.5241` | `0.5241` | `0.9756` | DTC C0291 - Brake Pedal Apply Sensor Circuit Malfunction | `C0291` | brakes_and_suspension |
| 2 | `VTR-C0081` | `0.5153` | `0.5153` | `0.9846` | DTC C0081 - ABS Malfunction Indicator | `C0081` | brakes_and_suspension |
| 3 | `VTR-C0082` | `0.5102` | `0.5102` | `0.9897` | DTC C0082 - Brake System Malfunction Indicator | `C0082` | brakes_and_suspension |
| 4 | `VTR-C0241` | `0.5097` | `0.5097` | `0.9903` | DTC C0241 - ABS Warning Lamp Control Circuit | `C0241` | brakes_and_suspension |
| 5 | `VTR-C0075` | `0.5019` | `0.5019` | `0.9980` | DTC C0075 - Brake Pedal Position Performance | `C0075` | brakes_and_suspension |

### Query Q05: Automatic Transmission & Shift Solenoids
- **Query Text**: *"Automatic transmission delayed engagement into drive and harsh shuddering when shifting between second and third gears"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `2.847 ms` | Cosine: `2.094 ms` | Dot: `0.22 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P2711` | `0.4985` | `0.4985` | `1.0015` | DTC P2711 - Unexpected Mechanical Gear Disengagement | `P2711` | engine_and_transmission |
| 2 | `VTR-P0733` | `0.4476` | `0.4476` | `1.0511` | DTC P0733 - Gear 3 Incorrect Ratio | `P0733` | engine_and_transmission |
| 3 | `VTR-P2E14` | `0.4447` | `0.4447` | `1.0538` | DTC P2E14 - Gear Selection Actuator Position Sensor Circuit Intermittent/Erratic | `P2E14` | engine_and_transmission |
| 4 | `VTR-P0918` | `0.4376` | `0.4376` | `1.0606` | DTC P0918 - Gear Shift Position Circuit A Intermittent | `P0918` | engine_and_transmission |
| 5 | `VTR-P2701` | `0.4375` | `0.4375` | `1.0607` | DTC P2701 - Transmission Friction Element B Apply Time Range/Performance | `P2701` | engine_and_transmission |

### Query Q06: Engine Misfire & Cylinder Combustion Faults
- **Query Text**: *"Check engine light flashing with rough idling, severe loss of engine power, and heavy vehicle vibration under load"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `2.931 ms` | Cosine: `2.256 ms` | Dot: `0.286 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `0.6667` | Top-10 Jaccard = `0.8182`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-B0860` | `0.4506` | `0.4506` | `1.0483` | DTC B0860 - License Plate Lamp Circuit | `B0860` | electrical_and_body |
| 2 | `VTR-B00D3` | `0.4411` | `0.4411` | `1.0573` | DTC B00D3 - Restraint System Malfunction Indicator 2 | `B00D3` | electrical_and_body |
| 3 | `VTR-C05F2` | `0.4365` | `0.4365` | `1.0616` | DTC C05F2 - Rear Drive Shaft Speed Sensor Circuit Intermittent | `C05F2` | brakes_and_suspension |
| 4 | `VTR-P062F` | `0.4362` | `0.4362` | `1.0619` | DTC P062F - Internal Control Module EEPROM Error | `P062F` | engine_and_transmission |
| 5 | `VTR-B00D4` | `0.4267` | `0.4267` | `1.0708` | DTC B00D4 - Restraint System Malfunction Audible Indicator | `B00D4` | electrical_and_body |

### Query Q07: Fuel & Air Metering / Rich Mixture
- **Query Text**: *"Drastic drop in fuel economy with black smoke from exhaust and rich fuel mixture odor during acceleration"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `2.719 ms` | Cosine: `2.051 ms` | Dot: `0.235 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P2BD2` | `0.3551` | `0.3551` | `1.1357` | DTC P2BD2 - Exhaust Aftertreatment System A Leak | `P2BD2` | engine_and_transmission |
| 2 | `VTR-P20D5` | `0.3497` | `0.3497` | `1.1405` | DTC P20D5 - Exhaust Aftertreatment Fuel Injector B Stuck Open | `P20D5` | engine_and_transmission |
| 3 | `VTR-P20CF` | `0.3317` | `0.3317` | `1.1561` | DTC P20CF - Exhaust Aftertreatment Fuel Injector A Stuck Open | `P20CF` | engine_and_transmission |
| 4 | `VTR-P02ED` | `0.3312` | `0.3312` | `1.1565` | DTC P02ED - Diesel Intake Air Flow A Control System - Low Air Flow Detected | `P02ED` | engine_and_transmission |
| 5 | `VTR-P24A3` | `0.3301` | `0.3301` | `1.1575` | DTC P24A3 - Particulate Filter Restriction - Soot Accumulation (Bank 2) | `P24A3` | engine_and_transmission |

### Query Q08: CAN Bus & Inter-Module Network Communication
- **Query Text**: *"Instrument cluster displays multiple failure lamps with total loss of CAN communication between engine and transmission control modules"*
- **Subsystem**: `network_and_communication`
- **Latencies**: Euclidean: `2.682 ms` | Cosine: `2.067 ms` | Dot: `0.236 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-B0223` | `0.5029` | `0.5029` | `0.9971` | DTC B0223 - SRS Indicator Lamp Circuit Malfunction | `B0223` | electrical_and_body |
| 2 | `VTR-P0804` | `0.4999` | `0.4999` | `1.0001` | DTC P0804 - Upshift/Skip Shift Lamp Control Circuit | `P0804` | engine_and_transmission |
| 3 | `VTR-U0039` | `0.4997` | `0.4997` | `1.0003` | DTC U0039 - Vehicle Communication Bus B (+) Open | `U0039` | network_and_communication |
| 4 | `VTR-U007E` | `0.4898` | `0.4898` | `1.0102` | DTC U007E - Control Module Communication Bus L Off | `U007E` | network_and_communication |
| 5 | `VTR-U0094` | `0.4861` | `0.4861` | `1.0138` | DTC U0094 - Vehicle Communication Bus H (+) Open | `U0094` | network_and_communication |

### Query Q09: Supplemental Restraint System (SRS) & Airbag Circuit
- **Query Text**: *"Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring"*
- **Subsystem**: `electrical_and_body`
- **Latencies**: Euclidean: `2.823 ms` | Cosine: `2.029 ms` | Dot: `0.221 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-B0005` | `0.5344` | `0.5344` | `0.9650` | DTC B0005 - Collapsible Steering Column Deployment Control | `B0005` | electrical_and_body |
| 2 | `VTR-B0061` | `0.4730` | `0.4730` | `1.0267` | DTC B0061 - Passenger Seat Belt Tension Sensor | `B0061` | electrical_and_body |
| 3 | `VTR-B0001` | `0.4728` | `0.4728` | `1.0268` | DTC B0001 - Driver Frontal Stage 1 Deployment Control | `B0001` | electrical_and_body |
| 4 | `VTR-U047B` | `0.4662` | `0.4662` | `1.0333` | DTC U047B - Invalid Data Received From Restraints System Sensor K | `U047B` | network_and_communication |
| 5 | `VTR-B0051` | `0.4609` | `0.4609` | `1.0384` | DTC B0051 - First Row Center Seat Belt Sensor | `B0051` | electrical_and_body |

### Query Q10: Turbocharger Forced Induction & Boost Control
- **Query Text**: *"Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills"*
- **Subsystem**: `engine_and_transmission`
- **Latencies**: Euclidean: `2.732 ms` | Cosine: `2.011 ms` | Dot: `0.219 ms`
- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `1.0` | Cosine vs Euclidean Jaccard = `1.0` | Exact Rank Order Match = `True`
- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `1.0` | Top-10 Jaccard = `1.0`

#### Top-5 Retrieved Documents Across All Three Metrics
| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | `VTR-P0299` | `0.5293` | `0.5293` | `0.9702` | DTC P0299 - Turbocharger/Supercharger A Underboost Condition | `P0299` | engine_and_transmission |
| 2 | `VTR-P0048` | `0.5165` | `0.5165` | `0.9834` | DTC P0048 - Turbocharger/Supercharger Boost Control A Circuit High | `P0048` | engine_and_transmission |
| 3 | `VTR-P0046` | `0.5018` | `0.5018` | `0.9982` | DTC P0046 - Turbocharger/Supercharger Boost Control A Circuit Range/Performance | `P0046` | engine_and_transmission |
| 4 | `VTR-P0047` | `0.4983` | `0.4983` | `1.0017` | DTC P0047 - Turbocharger/Supercharger Boost Control A Circuit Low | `P0047` | engine_and_transmission |
| 5 | `VTR-P02CA` | `0.4916` | `0.4916` | `1.0084` | DTC P02CA - Turbocharger/Supercharger B Overboost Condition | `P02CA` | engine_and_transmission |
