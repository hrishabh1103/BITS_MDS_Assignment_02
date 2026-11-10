# Mathematical Vector Similarity Metrics Comparison

## BITS Pilani WILP — Modern Database Systems (Assignment 2)
**Project Title**: Vehicle Troubleshooting Assistant using ChromaDB and Retrieval-Augmented Generation (RAG)  
**Document**: Phase 5 Exhaustive Mathematical Similarity Evaluation  
**Dataset**: 9,532 authentic vehicle diagnostic records (`data/processed/vehicle_troubleshooting.json`)  
**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (Dimension $D = 384$, $L_2$-normalized)  
**Database**: ChromaDB persistent collection `vehicle_troubleshooting_kb` (Cosine distance space)

---

## 1. Executive Summary

In Modern Database Systems, vector similarity search operates by computing proximity metrics between high-dimensional dense representations of queries and documents. While approximate nearest neighbor (ANN) indexes like HNSW prioritize sub-linear query latency, database engineers must understand the exact mathematical behavior of fundamental vector distance functions.

This study implements and evaluates three core similarity metrics using pure vectorized NumPy:
1. **Euclidean Distance ($L_2$ norm)**
2. **Cosine Similarity**
3. **Dot Product (Inner Product)**

Every metric was exhaustively evaluated across all **9,532 records** for **10 realistic vehicle troubleshooting queries** at **$K=5$ and $K=10$** ($10 \times 3 \times 2 = \mathbf{60}$ total experimental configurations). Furthermore, a controlled synthetic experiment was conducted to demonstrate ranking divergence on unnormalized vectors, and empirical results were benchmarked against ChromaDB's HNSW approximate index.

---

## 2. Mathematical Formulations

Let $\mathbf{q} \in \mathbb{R}^D$ denote the query vector embedding, and let $\mathbf{x}_i \in \mathbb{R}^D$ denote the embedding vector of the $i$-th document ($i \in \{1, \dots, N\}$, where $N = 9,532$ and $D = 384$).

```mermaid
graph TD
    Q["Query Vector q (D=384)"] --> Euc["Euclidean Distance (L2)<br/>||x - q||_2"]
    Q --> Cos["Cosine Similarity<br/>(x . q) / (||x|| ||q||)"]
    Q --> Dot["Dot Product<br/>x . q"]
    
    Euc --> AscSort["Ascending Sort<br/>(Smallest distance first)"]
    Cos --> DescSort["Descending Sort<br/>(Highest similarity first)"]
    Dot --> DescSort
    
    AscSort --> TopK["Top-K Retrieved Diagnostic Records (K=5, K=10)"]
    DescSort --> TopK
```

### 2.1 Euclidean Distance ($L_2$ Norm)

Euclidean distance measures the geometric straight-line separation between two vectors in Euclidean hyperspace:

$$d_{L_2}(\mathbf{x}_i, \mathbf{q}) = \|\mathbf{x}_i - \mathbf{q}\|_2 = \sqrt{\sum_{j=1}^D (x_{i,j} - q_j)^2}$$

- **Ranking Direction**: **Ascending** (smaller distance indicates higher semantic proximity; $d = 0$ signifies identical vectors).
- **Domain**: $[0, +\infty)$.
- **NumPy Vectorized Implementation**:
  ```python
  def euclidean_distance(documents: np.ndarray, query: np.ndarray) -> np.ndarray:
      return np.linalg.norm(documents - query, axis=1)
  ```

### 2.2 Cosine Similarity

Cosine similarity calculates the cosine of the angle $\theta$ between two vectors, effectively measuring directional alignment regardless of vector magnitudes:

$$\cos(\mathbf{x}_i, \mathbf{q}) = \frac{\mathbf{x}_i \cdot \mathbf{q}}{\|\mathbf{x}_i\|_2 \|\mathbf{q}\|_2} = \frac{\sum_{j=1}^D x_{i,j} q_j}{\sqrt{\sum_{j=1}^D x_{i,j}^2} \sqrt{\sum_{j=1}^D q_j^2}}$$

- **Ranking Direction**: **Descending** (larger score indicates higher semantic similarity; $+1.0$ indicates parallel vectors, $0.0$ orthogonal, $-1.0$ diametrically opposed).
- **Domain**: $[-1.0, +1.0]$.
- **NumPy Vectorized Implementation**:
  ```python
  def cosine_similarity(documents: np.ndarray, query: np.ndarray, eps: float = 1e-12) -> np.ndarray:
      dot_products = documents @ query
      doc_norms = np.linalg.norm(documents, axis=1)
      query_norm = np.linalg.norm(query)
      denominator = np.maximum(doc_norms * query_norm, eps)
      return np.clip(dot_products / denominator, -1.0, 1.0)
  ```

### 2.3 Dot Product (Inner Product)

The dot product is the sum of the element-wise products of the two vectors:

$$\mathbf{x}_i \cdot \mathbf{q} = \sum_{j=1}^D x_{i,j} q_j$$

- **Ranking Direction**: **Descending** (larger value indicates higher inner-product proximity).
- **Domain**: $(-\infty, +\infty)$ on unnormalized vectors; $[-1.0, +1.0]$ on unit vectors.
- **NumPy Vectorized Implementation**:
  ```python
  def dot_product(documents: np.ndarray, query: np.ndarray) -> np.ndarray:
      return documents @ query
  ```

---

## 3. Vector Normalization Theory & Mathematical Equivalence

A critical architectural consideration in modern vector search engines is **vector normalization**. In our system, the `sentence-transformers/all-MiniLM-L6-v2` model is configured with `normalize_embeddings=True`, guaranteeing that:

$$\|\mathbf{x}_i\|_2 = 1.0 \quad (\forall i \in \{1, \dots, N\}) \quad \text{and} \quad \|\mathbf{q}\|_2 = 1.0$$

### 3.1 Theorem 1: Identity of Cosine Similarity and Dot Product on Unit Vectors

When $\|\mathbf{x}_i\|_2 = 1.0$ and $\|\mathbf{q}\|_2 = 1.0$, the denominator of the cosine similarity reduces to 1:

$$\cos(\mathbf{x}_i, \mathbf{q}) = \frac{\mathbf{x}_i \cdot \mathbf{q}}{\|\mathbf{x}_i\|_2 \|\mathbf{q}\|_2} = \frac{\mathbf{x}_i \cdot \mathbf{q}}{1.0 \times 1.0} \equiv \mathbf{x}_i \cdot \mathbf{q}$$

**Consequence**: On unit-normalized embeddings, Cosine Similarity and Dot Product produce **identical scalar scores** and **identical ranking orders** ($\text{Jaccard} = 1.0$, exact rank match = 100%).

### 3.2 Theorem 2: Monotonic Equivalence with Euclidean Distance

Expanding the squared Euclidean distance between two unit vectors reveals its direct relationship with cosine similarity:

$$\|\mathbf{x}_i - \mathbf{q}\|_2^2 = (\mathbf{x}_i - \mathbf{q}) \cdot (\mathbf{x}_i - \mathbf{q}) = \|\mathbf{x}_i\|_2^2 + \|\mathbf{q}\|_2^2 - 2 (\mathbf{x}_i \cdot \mathbf{q})$$

Substituting $\|\mathbf{x}_i\|_2^2 = 1.0$, $\|\mathbf{q}\|_2^2 = 1.0$, and $\mathbf{x}_i \cdot \mathbf{q} = \cos(\mathbf{x}_i, \mathbf{q})$:

$$\|\mathbf{x}_i - \mathbf{q}\|_2^2 = 1 + 1 - 2 \cos(\mathbf{x}_i, \mathbf{q}) = 2\left(1 - \cos(\mathbf{x}_i, \mathbf{q})\right)$$

Taking the square root:

$$d_{L_2}(\mathbf{x}_i, \mathbf{q}) = \sqrt{2\left(1 - \cos(\mathbf{x}_i, \mathbf{q})\right)}$$

Let $f(s) = \sqrt{2(1 - s)}$ for $s \in [-1, 1]$. The derivative is:

$$f'(s) = \frac{-2}{2\sqrt{2(1 - s)}} = -\frac{1}{\sqrt{2(1 - s)}} < 0 \quad (\forall s < 1)$$

Since $f'(s) < 0$ strictly across the domain, $f(s)$ is a **strictly monotonically decreasing function**. 

**Consequence**: Sorting documents in ascending order of Euclidean distance ($d_{L_2} \uparrow$) produces the **exact same permutation** as sorting in descending order of Cosine similarity ($\cos \downarrow$) and Dot product ($\cdot \downarrow$).

---

## 4. Synthetic Metric Divergence Experiment (Unnormalized Vectors)

To demonstrate when and why the three metrics produce radically divergent rankings, a controlled experiment was conducted on synthetic unnormalized vectors where magnitude and direction were intentionally decoupled.

### Experimental Setup
- **Query $\mathbf{q}$**: `[1.0, 0.0]` (unit vector pointing along x-axis)
- **Doc A (collinear, unit)**: `[1.0, 0.0]` ($\|\mathbf{x}\| = 1.0, \theta = 0^\circ$)
- **Doc B (collinear, huge)**: `[10.0, 0.0]` ($\|\mathbf{x}\| = 10.0, \theta = 0^\circ$)
- **Doc C (small, angled)**: `[0.9, 0.2]` ($\|\mathbf{x}\| \approx 0.92, \theta \approx 12.5^\circ$)
- **Doc D (huge, orthogonal)**: `[0.0, 10.0]` ($\|\mathbf{x}\| = 10.0, \theta = 90.0^\circ$)

### Synthetic Results Comparison Table

| Document | Vector Coordinates | Euclidean Distance Rank (Score) | Cosine Similarity Rank (Score) | Dot Product Rank (Score) |
|:---|:---:|:---:|:---:|:---:|
| **Doc A (unit, collinear)** | `[1.0, 0.0]` | **#1 (0.0000)** | **#1 (1.0000)** | #2 (1.0000) |
| **Doc B (huge, collinear)** | `[10.0, 0.0]` | #3 (9.0000) | **#1 (1.0000)** | **#1 (10.0000)** |
| **Doc C (small, angled)** | `[0.9, 0.2]` | #2 (0.2236) | #3 (0.9762) | #3 (0.9000) |
| **Doc D (huge, orthogonal)**| `[0.0, 10.0]`| #4 (10.0499) | #4 (0.0000) | #4 (0.0000) |

> [!NOTE]
> **Key Analytical Insights**:
> 1. **Dot Product is dominated by magnitude**: Doc B achieves an inner product of $10.0$, dwarfing Doc A ($1.0$), solely because its length is 10 times larger. In text retrieval without normalization, long verbose documents would artificially dominate short relevant documents.
> 2. **Euclidean distance penalizes magnitude disparity**: Although Doc B points in the exact direction of the query, its Euclidean distance is $9.0$, causing it to rank behind Doc C (distance $0.22$).
> 3. **Cosine similarity isolates semantic direction**: Cosine assigns both Doc A and Doc B a perfect similarity of $1.0000$, correctly identifying their collinear orientation regardless of scale.
> 4. **When normalized**: All vectors are projected onto the unit hypersphere, collapsing Doc A and Doc B into the identical vector and rendering all three rankings identical.

---

## 5. Exhaustive Query Retrieval Results (Q01 – Q10)

Across all 10 queries, exhaustive NumPy evaluations on the 9,532 authentic vehicle records yielded the following retrieval results for $K=5$ and $K=10$:

| Query ID | Subsystem | Top-1 Record ID | Top-1 DTC | Metric Agreement (K=5) | Metric Agreement (K=10) | Exact Order Match |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **Q01** | `engine_and_transmission` | `VTR-P00B7` | P00B7 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q02** | `engine_and_transmission` | `VTR-P0316` | P0316 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q03** | `electrical_and_body` | `VTR-P0D17` | P0D17 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q04** | `brakes_and_suspension` | `VTR-C0291` | C0291 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q05** | `engine_and_transmission` | `VTR-P2711` | P2711 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q06** | `engine_and_transmission` | `VTR-B0860` | B0860 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q07** | `engine_and_transmission` | `VTR-P2BD2` | P2BD2 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q08** | `electrical_and_body` | `VTR-B0223` | B0223 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q09** | `electrical_and_body` | `VTR-B0005` | B0005 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |
| **Q10** | `engine_and_transmission` | `VTR-P0299` | P0299 | Jaccard = 1.0 | Jaccard = 1.0 | **100% Match** |

> [!IMPORTANT]
> **Empirical Validation of Theory & Phase 4 Cross-Verification**:
> For **all 10 queries**, Euclidean distance, Cosine similarity, and Dot Product produced **100% identical top-5 and top-10 ranked sequences** on the authentic normalized dataset. This empirically verifies Theorems 1 and 2.
> 
> Furthermore, cross-verification with Phase 4's ground-truth retrieval artifacts (`experiments/semantic_search_results.json`) confirms that **all 10 Top-1 documents retrieved in Phase 5 match Phase 4 exactly**. Detailed cryptographic vector fingerprinting and reconciliation is documented in [`experiments/phase4_phase5_reconciliation.md`](file:///Users/hrishabh/BITS_MDS_Assignment_02/experiments/phase4_phase5_reconciliation.md).

---

## 6. Exact kNN (NumPy) vs Approximate kNN (ChromaDB HNSW)

A foundational topic in Modern Database Systems is the trade-off between **Exact Exhaustive Search (Linear Scan)** and **Approximate Nearest Neighbor Search (ANN Graphs)**.

```mermaid
graph LR
    subgraph "Exhaustive Linear Scan (Pure NumPy)"
        NS[Query] -->|Scan all 9,532 records| SCAN["O(N * D) Brute Force Matrix Multiply"]
        SCAN --> EXACT["100% Recall (Exact kNN Ground Truth)"]
    end
    subgraph "Approximate Nearest Neighbor (ChromaDB HNSW)"
        CS[Query] -->|Multi-layer Skip Graph| HNSW["O(log N) Heuristic Graph Traversal"]
        HNSW --> APPROX["Sub-linear Speed (Recall ~95-100%)"]
    end
```

### Empirical Cross-System Comparison

| Query | ChromaDB vs NumPy (Top-5 Jaccard) | ChromaDB vs NumPy (Top-10 Jaccard) | Identical Permutation? | Observed Behavioral Difference |
|:---:|:---:|:---:|:---:|:---|
| **Q01** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q02** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q03** | **1.0000** | **0.8182** | False | Top 8 identical; ranks 9 and 10 differed slightly due to graph pruning. |
| **Q04** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q05** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q06** | **0.6667** | **0.8182** | False | Top 3 identical; rank 4 score difference was $\Delta = 0.00034$, pruned in HNSW. |
| **Q07** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q08** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q09** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |
| **Q10** | **1.0000** | **1.0000** | **True** | Perfect agreement on all 10 ranks. |

### Technical Analysis of Divergence on Q06
In Query Q06 (*"Check engine light flashing with rough idling, severe loss of engine power..."*):
- **NumPy Rank 3**: `VTR-C05F2` ($\text{score} = 0.436545$)
- **NumPy Rank 4**: `VTR-P062F` ($\text{score} = 0.436201$)
- **NumPy Rank 5**: `VTR-B00D4` ($\text{score} = 0.426663$)

The score difference between Rank 3 and Rank 4 is merely **$0.000344$**. In ChromaDB's HNSW graph, the traversal uses a finite beam width (`ef_search`). Because `VTR-P062F` belonged to a neighboring cluster separated by an intermediate cluster boundary in the Delaunay graph, the heuristic search did not explore that branch, instead retrieving `VTR-B00D4` (score $0.4266$).

This provides an authentic real-world demonstration of the **Recall vs Speed trade-off**:
- **NumPy Linear Scan**: Provides the 100% exact ground truth ($1.0$ recall), but runtime scales linearly with dataset size: $O(N \cdot D)$.
- **ChromaDB HNSW**: Provides near-instant sub-linear queries ($O(\log N)$), but introduces small recall variations when clusters are tightly packed.

---

## 7. Computational Complexity & Execution Benchmarks

### 7.1 Algorithmic Complexity

| Operation | Time Complexity | Auxiliary Space Complexity | Memory Footprint (9,532 records, $D=384$) |
|:---|:---:|:---:|:---|
| **Dot Product** | $O(N \cdot D)$ | $O(N)$ | $9532 \times 384 \times 4 \text{ bytes} \approx \mathbf{14.64 \text{ MB}}$ |
| **Cosine Similarity** | $O(N \cdot D) + O(N)$ | $O(N)$ | $14.64 \text{ MB} + \text{norms } (38 \text{ KB})$ |
| **Euclidean Distance** | $O(N \cdot D)$ | $O(N \cdot D)$ *(diff matrix)* | $\approx 29.28 \text{ MB}$ during broadcasting subtraction |

### 7.2 Empirical Latency Benchmarks (CPU, Single Query vs 9,532 Vectors)

| Metric | Mean Latency | Min Latency | Max Latency | Standard Deviation |
|:---|:---:|:---:|:---:|:---:|
| **Dot Product** | **$0.25 \text{ ms}$** | $0.22 \text{ ms}$ | $0.36 \text{ ms}$ | $0.04 \text{ ms}$ |
| **Cosine Similarity** | **$2.14 \text{ ms}$** | $2.01 \text{ ms}$ | $2.51 \text{ ms}$ | $0.16 \text{ ms}$ |
| **Euclidean Distance** | **$3.44 \text{ ms}$** | $2.68 \text{ ms}$ | $7.65 \text{ ms}$ | $1.44 \text{ ms}$ |

### 7.3 Performance Explanation
1. **Dot Product is $8.5\times$ faster than Cosine and $13.7\times$ faster than Euclidean**:
   - Executes as a single, highly optimized BLAS Level 2 matrix-vector multiplication (`dgemv` / `sgemv`), leveraging SIMD vector registers and CPU cache lines.
2. **Cosine Similarity introduces overhead**:
   - Computing row-wise norms requires $N$ square root operations and $N$ floating-point division operations.
3. **Euclidean Distance is slowest in naive NumPy**:
   - Broadcasting `(documents - query)` allocates a temporary $9532 \times 384$ difference matrix in memory, followed by element-wise squaring, summing along axis 1, and taking square roots.

---

## 8. Viva Voce Preparation & Examiner Defense

### Q1: Why did all three metrics produce identical rankings for your 10 assignment queries?
> **Answer**: Because all document embeddings and query embeddings were $L_2$-normalized to unit length ($\|\mathbf{x}\|_2 = 1.0$). Mathematically, $\cos(\mathbf{x}, \mathbf{q}) = \frac{\mathbf{x} \cdot \mathbf{q}}{\|\mathbf{x}\|_2 \|\mathbf{q}\|_2} = \mathbf{x} \cdot \mathbf{q}$, so Cosine similarity and Dot product are strictly identical. Furthermore, Euclidean distance expands to $d_{L_2} = \sqrt{2(1 - \cos(\mathbf{x}, \mathbf{q}))}$, which is a strictly monotonically decreasing function of cosine similarity. Sorting in ascending order of Euclidean distance mathematically yields the exact same permutation as sorting in descending order of Cosine similarity.

### Q2: What would happen if embeddings were not normalized?
> **Answer**: On unnormalized vectors, Dot product favors vectors with large magnitudes, even if they point in a different direction. Euclidean distance penalizes magnitude differences, favoring vectors close to the query in coordinate space. Only Cosine similarity remains invariant to vector length, isolating the pure angular alignment. We demonstrated this in our synthetic experiment where a collinear vector with $10\times$ magnitude ranked #1 in Dot product ($10.0$) but dropped to #3 in Euclidean distance ($9.0$), whereas Cosine scored both at $1.0000$.

### Q3: Why did ChromaDB results differ on Query Q06 from your NumPy results?
> **Answer**: ChromaDB uses an Approximate Nearest Neighbor (ANN) index based on Hierarchical Navigable Small World (HNSW) graphs, whereas our NumPy implementation performs an exact exhaustive linear scan ($O(N \cdot D)$). On Q06, two candidates differed in cosine similarity by only $0.000344$. HNSW's heuristic graph search pruned one of the graph paths to preserve sub-millisecond retrieval speed, demonstrating the classic database trade-off between 100% recall and query latency.

---
*Generated and verified as part of BITS Pilani Modern Database Systems Assignment 2 (Phase 5).*

