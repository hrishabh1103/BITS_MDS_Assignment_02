"""Comprehensive similarity metrics comparison script for Vehicle Troubleshooting Assistant.

Performs exhaustive NumPy similarity comparisons across all 9,532 dataset records for
the 10 assignment queries using Euclidean distance (L2), Cosine similarity, and Dot Product
at K=5 and K=10 (60 total configurations). Validates mathematical equivalence on unit-normalized
embeddings and demonstrates ranking divergence on synthetic unnormalized vectors.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List
import numpy as np

from src.chroma_manager import ChromaDBManager
from src.config import BASE_DIR, EXPERIMENTS_DIR
from src.similarity_metrics import (
    compare_rankings,
    euclidean_distance,
    cosine_similarity,
    dot_product,
    rank_documents,
    run_synthetic_metric_divergence_experiment,
)
from src.utils import setup_logger

logger = setup_logger("run_similarity_comparison")


def load_assignment_queries() -> List[Dict[str, Any]]:
    """Loads the 10 defined assignment queries from data/queries/assignment_queries.json."""
    queries_path = BASE_DIR / "data" / "queries" / "assignment_queries.json"
    if not queries_path.exists():
        raise FileNotFoundError(f"Queries file not found at '{queries_path}'")
    with open(queries_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
    logger.info(f"Loaded {len(queries)} assignment queries from '{queries_path}'.")
    return queries


def load_phase4_chroma_results() -> Dict[str, Any]:
    """Loads Phase 4 ChromaDB search results for cross-system comparison."""
    results_path = EXPERIMENTS_DIR / "semantic_search_results.json"
    if not results_path.exists():
        logger.warning(f"Phase 4 results not found at '{results_path}'. Skipping Chroma cross-comparison.")
        return {}
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {q["query_id"]: q for q in data.get("queries", [])}


def main():
    logger.info("=" * 70)
    logger.info("STARTING PHASE 5: NUMPY EXHAUSTIVE SIMILARITY COMPARISON")
    logger.info("=" * 70)

    # 1. Initialize ChromaDB Manager and load all records
    logger.info("Connecting to ChromaDB and extracting 9,532 document embeddings...")
    chroma_mgr = ChromaDBManager()
    total_docs = chroma_mgr.get_count()
    logger.info(f"Total documents in ChromaDB collection '{chroma_mgr.collection_name}': {total_docs}")

    t_fetch_start = time.perf_counter()
    all_data = chroma_mgr.collection.get(include=["embeddings", "metadatas", "documents"])
    t_fetch_end = time.perf_counter()

    doc_ids = all_data["ids"]
    doc_metadatas = {doc_ids[i]: all_data["metadatas"][i] for i in range(len(doc_ids))}
    doc_texts = {doc_ids[i]: all_data["documents"][i] for i in range(len(doc_ids))}
    doc_embeddings = np.array(all_data["embeddings"], dtype=np.float32)

    logger.info(
        f"Successfully loaded {len(doc_ids)} embeddings of dimension {doc_embeddings.shape[1]} "
        f"in {round((t_fetch_end - t_fetch_start) * 1000, 2)} ms."
    )

    # Verify L2 normalization of document embeddings
    doc_norms = np.linalg.norm(doc_embeddings, axis=1)
    is_doc_normalized = bool(np.allclose(doc_norms, 1.0, atol=1e-5))
    logger.info(f"Document embeddings unit-normalized (||x||_2 == 1.0): {is_doc_normalized}")

    # 2. Load Queries and Phase 4 results
    queries = load_assignment_queries()
    phase4_results = load_phase4_chroma_results()

    # 3. Execute Similarity Comparisons
    results_payload: Dict[str, Any] = {
        "metadata": {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_queries": len(queries),
            "total_documents": len(doc_ids),
            "embedding_dimension": int(doc_embeddings.shape[1]),
            "embedding_model": chroma_mgr.embedding_manager.model_name,
            "document_embeddings_normalized": is_doc_normalized,
            "metrics_evaluated": ["euclidean_l2", "cosine_similarity", "dot_product"],
            "k_values": [5, 10],
            "total_evaluations": len(queries) * 3 * 2,
        },
        "query_evaluations": [],
        "metric_latency_summary": {},
        "synthetic_divergence_experiment": run_synthetic_metric_divergence_experiment(),
    }

    latencies: Dict[str, List[float]] = {
        "euclidean": [],
        "cosine": [],
        "dot_product": [],
    }

    for q in queries:
        qid = q["query_id"]
        qtext = q["query_text"]
        logger.info(f"\n--- Evaluating Query {qid}: '{qtext[:65]}...' ---")

        # Generate query embedding
        q_emb = chroma_mgr.embedding_manager.embed_query(qtext, normalize=True)
        q_norm = float(np.linalg.norm(q_emb))
        is_q_normalized = bool(np.isclose(q_norm, 1.0, atol=1e-5))

        # Metric 1: Euclidean Distance (L2)
        t0 = time.perf_counter()
        euc_scores = euclidean_distance(doc_embeddings, q_emb)
        t_euc = (time.perf_counter() - t0) * 1000.0
        latencies["euclidean"].append(t_euc)

        # Metric 2: Cosine Similarity
        t0 = time.perf_counter()
        cos_scores = cosine_similarity(doc_embeddings, q_emb)
        t_cos = (time.perf_counter() - t0) * 1000.0
        latencies["cosine"].append(t_cos)

        # Metric 3: Dot Product
        t0 = time.perf_counter()
        dot_scores = dot_product(doc_embeddings, q_emb)
        t_dot = (time.perf_counter() - t0) * 1000.0
        latencies["dot_product"].append(t_dot)

        # Compute rankings for K=5 and K=10
        rankings_k5 = {
            "euclidean": rank_documents(euc_scores, "euclidean", doc_ids, top_k=5),
            "cosine": rank_documents(cos_scores, "cosine", doc_ids, top_k=5),
            "dot_product": rank_documents(dot_scores, "dot_product", doc_ids, top_k=5),
        }

        rankings_k10 = {
            "euclidean": rank_documents(euc_scores, "euclidean", doc_ids, top_k=10),
            "cosine": rank_documents(cos_scores, "cosine", doc_ids, top_k=10),
            "dot_product": rank_documents(dot_scores, "dot_product", doc_ids, top_k=10),
        }

        # Helper to format rich item dict
        def enrich_ranking(ranked_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            enriched = []
            for item in ranked_items:
                rec_id = item["record_id"]
                meta = doc_metadatas.get(rec_id, {})
                doc_str = doc_texts.get(rec_id, "")
                excerpt = ""
                for line in doc_str.split("\n"):
                    if line.startswith("Problem Description:"):
                        excerpt = line.replace("Problem Description:", "").strip()
                        break
                if not excerpt and doc_str:
                    excerpt = doc_str.split("\n")[0]

                enriched.append({
                    "rank": item["rank"],
                    "record_id": rec_id,
                    "score": round(item["score"], 6),
                    "title": meta.get("title", ""),
                    "diagnostic_codes": meta.get("diagnostic_codes", ""),
                    "vehicle_system": meta.get("vehicle_system", ""),
                    "severity": meta.get("severity", ""),
                    "excerpt": excerpt[:200] + ("..." if len(excerpt) > 200 else ""),
                })
            return enriched

        # Pairwise overlap comparisons at K=5 and K=10
        ids_euc_5 = [x["record_id"] for x in rankings_k5["euclidean"]]
        ids_cos_5 = [x["record_id"] for x in rankings_k5["cosine"]]
        ids_dot_5 = [x["record_id"] for x in rankings_k5["dot_product"]]

        ids_euc_10 = [x["record_id"] for x in rankings_k10["euclidean"]]
        ids_cos_10 = [x["record_id"] for x in rankings_k10["cosine"]]
        ids_dot_10 = [x["record_id"] for x in rankings_k10["dot_product"]]

        overlap_k5 = {
            "cosine_vs_dot": compare_rankings(ids_cos_5, ids_dot_5),
            "cosine_vs_euclidean": compare_rankings(ids_cos_5, ids_euc_5),
            "dot_vs_euclidean": compare_rankings(ids_dot_5, ids_euc_5),
        }

        overlap_k10 = {
            "cosine_vs_dot": compare_rankings(ids_cos_10, ids_dot_10),
            "cosine_vs_euclidean": compare_rankings(ids_cos_10, ids_euc_10),
            "dot_vs_euclidean": compare_rankings(ids_dot_10, ids_euc_10),
        }

        # ChromaDB cross-verification (if Phase 4 results available)
        chroma_cross_check = {}
        if qid in phase4_results:
            p4_top5_ids = [r["id"] for r in phase4_results[qid].get("top_5", [])]
            p4_top10_ids = [r["id"] for r in phase4_results[qid].get("top_10", [])]
            chroma_cross_check = {
                "top_5_match_with_chroma": compare_rankings(ids_cos_5, p4_top5_ids),
                "top_10_match_with_chroma": compare_rankings(ids_cos_10, p4_top10_ids),
            }

        q_entry = {
            "query_id": qid,
            "query_text": qtext,
            "topic": q["topic"],
            "subsystem": q["subsystem"],
            "query_embedding_normalized": is_q_normalized,
            "computation_latencies_ms": {
                "euclidean": round(t_euc, 3),
                "cosine": round(t_cos, 3),
                "dot_product": round(t_dot, 3),
            },
            "rankings_k5": {
                "euclidean": enrich_ranking(rankings_k5["euclidean"]),
                "cosine": enrich_ranking(rankings_k5["cosine"]),
                "dot_product": enrich_ranking(rankings_k5["dot_product"]),
            },
            "rankings_k10": {
                "euclidean": enrich_ranking(rankings_k10["euclidean"]),
                "cosine": enrich_ranking(rankings_k10["cosine"]),
                "dot_product": enrich_ranking(rankings_k10["dot_product"]),
            },
            "pairwise_comparisons": {
                "k5": overlap_k5,
                "k10": overlap_k10,
            },
            "chroma_cross_verification": chroma_cross_check,
        }
        results_payload["query_evaluations"].append(q_entry)

        # Log summary for this query
        logger.info(
            f"  Latencies: Euc={round(t_euc, 2)}ms | Cos={round(t_cos, 2)}ms | Dot={round(t_dot, 2)}ms"
        )
        logger.info(
            f"  Top-1 Rank: Euc={ids_euc_5[0]} | Cos={ids_cos_5[0]} | Dot={ids_dot_5[0]}"
        )
        logger.info(
            f"  Top-5 Perfect Rank Match (Cos vs Dot vs Euc): "
            f"{overlap_k5['cosine_vs_dot']['exact_order_match'] and overlap_k5['cosine_vs_euclidean']['exact_order_match']}"
        )

    # 4. Latency summaries across all 10 queries
    for m in ["euclidean", "cosine", "dot_product"]:
        times = latencies[m]
        results_payload["metric_latency_summary"][m] = {
            "mean_ms": round(float(np.mean(times)), 3),
            "min_ms": round(float(np.min(times)), 3),
            "max_ms": round(float(np.max(times)), 3),
            "std_ms": round(float(np.std(times)), 3),
        }

    # 5. Save JSON results
    json_out_path = EXPERIMENTS_DIR / "similarity_comparison_results.json"
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    logger.info(f"\nSaved structured similarity comparison results to '{json_out_path}'.")

    # 6. Generate Markdown Report
    generate_markdown_report(results_payload)

    # 7. Verify collection count preserved
    final_count = chroma_mgr.get_count()
    assert final_count == 9532, f"Chroma collection count changed! Expected 9532, got {final_count}"
    logger.info(f"Verified ChromaDB collection count post-experiment: {final_count} (strictly preserved).")
    logger.info("=" * 70)
    logger.info("PHASE 5 NUMPY SIMILARITY COMPARISON COMPLETE")
    logger.info("=" * 70)


def generate_markdown_report(data: Dict[str, Any]) -> None:
    """Generates an extensive academic markdown report documenting Phase 5 results."""
    md_out_path = EXPERIMENTS_DIR / "similarity_comparison_results.md"
    meta = data["metadata"]
    lat_summary = data["metric_latency_summary"]
    synth = data["synthetic_divergence_experiment"]
    queries = data["query_evaluations"]

    lines: List[str] = [
        "# Phase 5: Exhaustive NumPy Similarity Metrics Comparison Report",
        "",
        "## Modern Database Systems (Assignment 2) — Academic Evaluation",
        "",
        f"- **Execution Timestamp**: `{meta['execution_timestamp']}`",
        f"- **Dataset Size**: `{meta['total_documents']:,}` authentic diagnostic records",
        f"- **Embedding Model**: `{meta['embedding_model']}`",
        f"- **Embedding Dimension**: `{meta['embedding_dimension']}`",
        f"- **Vector Normalization**: Document Embeddings = `||x||_2 = 1.0` (`{meta['document_embeddings_normalized']}`), Query Embeddings = `||q||_2 = 1.0`",
        f"- **Metrics Evaluated**: Euclidean Distance ($L_2$), Cosine Similarity, Dot Product",
        f"- **Configurations Evaluated**: 10 Queries $\\times$ 3 Metrics $\\times$ 2 Cutoffs ($K=5, K=10$) = **60 evaluations**",
        "",
        "---",
        "",
        "## 1. Mathematical Foundations & Metric Formulations",
        "",
        "For a query vector $\\mathbf{q} \\in \\mathbb{R}^D$ and document vector $\\mathbf{x}_i \\in \\mathbb{R}^D$:",
        "",
        "### A. Euclidean Distance ($L_2$ Norm)",
        "$$\\text{dist}_{L_2}(\\mathbf{x}_i, \\mathbf{q}) = \\|\\mathbf{x}_i - \\mathbf{q}\\|_2 = \\sqrt{\\sum_{j=1}^D (x_{i,j} - q_j)^2}$$",
        "- **Direction**: Ascending sort (smaller distance denotes higher semantic proximity).",
        "- **Geometric Property**: Measures absolute geometric distance in Euclidean hyperspace.",
        "",
        "### B. Cosine Similarity",
        "$$\\cos(\\mathbf{x}_i, \\mathbf{q}) = \\frac{\\mathbf{x}_i \\cdot \\mathbf{q}}{\\|\\mathbf{x}_i\\|_2 \\|\\mathbf{q}\\|_2} = \\frac{\\sum_{j=1}^D x_{i,j} q_j}{\\sqrt{\\sum_{j=1}^D x_{i,j}^2} \\sqrt{\\sum_{j=1}^D q_j^2}}$$",
        "- **Direction**: Descending sort (higher score denotes closer angular alignment).",
        "- **Range**: $[-1.0, 1.0]$.",
        "",
        "### C. Dot Product (Inner Product)",
        "$$\\mathbf{x}_i \\cdot \\mathbf{q} = \\sum_{j=1}^D x_{i,j} q_j$$",
        "- **Direction**: Descending sort (higher value denotes higher inner product).",
        "- **Magnitude Sensitivity**: Scales directly with the magnitudes $\\|\\mathbf{x}_i\\|_2$ and $\\|\\mathbf{q}\\|_2$.",
        "",
        "---",
        "",
        "## 2. Impact of Vector Normalization ($L_2$ Unit Norms)",
        "",
        "When vector embeddings are normalized such that $\\|\\mathbf{x}_i\\|_2 = 1.0$ and $\\|\\mathbf{q}\\|_2 = 1.0$:",
        "",
        "1. **Identity of Cosine Similarity and Dot Product**:",
        "   $$\\cos(\\mathbf{x}_i, \\mathbf{q}) = \\frac{\\mathbf{x}_i \\cdot \\mathbf{q}}{1.0 \\times 1.0} = \\mathbf{x}_i \\cdot \\mathbf{q}$$",
        "   Cosine similarity and Dot Product yield numerically identical scores and identical rankings.",
        "",
        "2. **Strict Monotonic Equivalence with Euclidean Distance**:",
        "   $$\\|\\mathbf{x}_i - \\mathbf{q}\\|_2^2 = \\|\\mathbf{x}_i\\|_2^2 + \\|\\mathbf{q}\\|_2^2 - 2 (\\mathbf{x}_i \\cdot \\mathbf{q}) = 1 + 1 - 2 \\cos(\\mathbf{x}_i, \\mathbf{q}) = 2(1 - \\cos(\\mathbf{x}_i, \\mathbf{q}))$$",
        "   $$\\text{dist}_{L_2}(\\mathbf{x}_i, \\mathbf{q}) = \\sqrt{2(1 - \\cos(\\mathbf{x}_i, \\mathbf{q}))}$$",
        "   Because $\\sqrt{2(1 - s)}$ is a strictly monotonically decreasing function of $s = \\cos(\\mathbf{x}_i, \\mathbf{q})$ on $[-1, 1]$, sort order is preserved identically: sorting in ascending order of Euclidean distance yields the exact same permutation as sorting in descending order of Cosine similarity.",
        "",
        "---",
        "",
        "## 3. Synthetic Metric Divergence Experiment (Unnormalized Vectors)",
        "",
        "To illustrate the divergence of metrics when vector lengths vary, a controlled synthetic experiment was executed:",
        "- **Query $\\mathbf{q}$**: `[1.0, 0.0]` (unit vector along x-axis)",
        "- **Doc A (collinear, unit)**: `[1.0, 0.0]` (norm = 1.0, angle = 0°)",
        "- **Doc B (collinear, huge)**: `[10.0, 0.0]` (norm = 10.0, angle = 0°)",
        "- **Doc C (small, angled)**: `[0.9, 0.2]` (norm = 0.92, angle = 12.5°)",
        "- **Doc D (huge, orthogonal)**: `[0.0, 10.0]` (norm = 10.0, angle = 90°)",
        "",
        "### Unnormalized Rankings Comparison Table",
        "| Document | Euclidean Rank (Score) | Cosine Rank (Score) | Dot Product Rank (Score) |",
        "|:---|:---:|:---:|:---:|",
    ]

    unnorm = synth["unnormalized"]
    euc_map = {x["record_id"]: (x["rank"], x["score"]) for x in unnorm["euclidean_ranking"]}
    cos_map = {x["record_id"]: (x["rank"], x["score"]) for x in unnorm["cosine_ranking"]}
    dot_map = {x["record_id"]: (x["rank"], x["score"]) for x in unnorm["dot_product_ranking"]}

    for doc_name in unnorm["documents"]:
        e_rank, e_score = euc_map[doc_name]
        c_rank, c_score = cos_map[doc_name]
        d_rank, d_score = dot_map[doc_name]
        lines.append(f"| **{doc_name}** | #{e_rank} ({e_score:.4f}) | #{c_rank} ({c_score:.4f}) | #{d_rank} ({d_score:.4f}) |")

    lines.extend([
        "",
        "> [!IMPORTANT]",
        "> **Key Analytical Observation**:",
        "> On unnormalized vectors, Dot Product ranks Doc B #1 with an overwhelming score of 10.0 purely due to its magnitude, even though Doc A is identical in orientation. Euclidean distance ranks Doc A #1 (distance 0.0) but pushes Doc B down to #3 (distance 9.0) because of length disparity. Cosine similarity correctly isolates orientation, ranking both Doc A and Doc B equally at 1.000. Once normalized, all three metrics produce identical rank order.",
        "",
        "---",
        "",
        "## 4. Empirical Performance & Computation Latency",
        "",
        "Full exhaustive matrix search across all 9,532 records (384 dimensions) on CPU:",
        "",
        "| Metric | Mean Latency (ms) | Min Latency (ms) | Max Latency (ms) | Std Dev (ms) |",
        "|:---|:---:|:---:|:---:|:---:|",
        f"| **Dot Product** | `{lat_summary['dot_product']['mean_ms']:.2f}` ms | `{lat_summary['dot_product']['min_ms']:.2f}` ms | `{lat_summary['dot_product']['max_ms']:.2f}` ms | `{lat_summary['dot_product']['std_ms']:.2f}` ms |",
        f"| **Cosine Similarity** | `{lat_summary['cosine']['mean_ms']:.2f}` ms | `{lat_summary['cosine']['min_ms']:.2f}` ms | `{lat_summary['cosine']['max_ms']:.2f}` ms | `{lat_summary['cosine']['std_ms']:.2f}` ms |",
        f"| **Euclidean Distance** | `{lat_summary['euclidean']['mean_ms']:.2f}` ms | `{lat_summary['euclidean']['min_ms']:.2f}` ms | `{lat_summary['euclidean']['max_ms']:.2f}` ms | `{lat_summary['euclidean']['std_ms']:.2f}` ms |",
        "",
        "- **Dot Product** is fastest because it executes as a single optimized BLAS matrix-vector product (`GEMV`).",
        "- **Cosine Similarity** requires additional norm calculations and floating-point divisions.",
        "- **Euclidean Distance** requires broadcasting subtraction, squaring, summation, and elementwise square roots across $9532 \\times 384$ entries.",
        "",
        "---",
        "",
        "## 5. Exhaustive Query Retrieval Results (Q01 – Q10)",
        "",
    ])

    for q in queries:
        qid = q["query_id"]
        qtext = q["query_text"]
        topic = q["topic"]
        subsystem = q["subsystem"]
        pk5 = q["pairwise_comparisons"]["k5"]
        pk10 = q["pairwise_comparisons"]["k10"]
        c_cross = q.get("chroma_cross_verification", {})

        lines.extend([
            f"### Query {qid}: {topic}",
            f"- **Query Text**: *\"{qtext}\"*",
            f"- **Subsystem**: `{subsystem}`",
            f"- **Latencies**: Euclidean: `{q['computation_latencies_ms']['euclidean']} ms` | Cosine: `{q['computation_latencies_ms']['cosine']} ms` | Dot: `{q['computation_latencies_ms']['dot_product']} ms`",
            f"- **Metric Agreement (K=5)**: Cosine vs Dot Jaccard = `{pk5['cosine_vs_dot']['jaccard_similarity']}` | Cosine vs Euclidean Jaccard = `{pk5['cosine_vs_euclidean']['jaccard_similarity']}` | Exact Rank Order Match = `{pk5['cosine_vs_euclidean']['exact_order_match']}`",
            f"- **Metric Agreement (K=10)**: Cosine vs Dot Jaccard = `{pk10['cosine_vs_dot']['jaccard_similarity']}` | Cosine vs Euclidean Jaccard = `{pk10['cosine_vs_euclidean']['jaccard_similarity']}` | Exact Rank Order Match = `{pk10['cosine_vs_euclidean']['exact_order_match']}`",
        ])

        if c_cross:
            t5_m = c_cross.get("top_5_match_with_chroma", {})
            t10_m = c_cross.get("top_10_match_with_chroma", {})
            lines.append(
                f"- **Cross-Verification with ChromaDB (HNSW Index)**: Top-5 Jaccard = `{t5_m.get('jaccard_similarity', 'N/A')}` | Top-10 Jaccard = `{t10_m.get('jaccard_similarity', 'N/A')}`"
            )

        lines.extend([
            "",
            "#### Top-5 Retrieved Documents Across All Three Metrics",
            "| Rank | Record ID | Cosine Sim | Dot Product | Euclidean Dist | Title | DTC | System |",
            "|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---|",
        ])

        top5_cos = q["rankings_k5"]["cosine"]
        top5_dot = q["rankings_k5"]["dot_product"]
        top5_euc = q["rankings_k5"]["euclidean"]

        for idx in range(len(top5_cos)):
            c_item = top5_cos[idx]
            d_item = top5_dot[idx]
            e_item = top5_euc[idx]
            lines.append(
                f"| {idx + 1} | `{c_item['record_id']}` | `{c_item['score']:.4f}` | `{d_item['score']:.4f}` | `{e_item['score']:.4f}` | {c_item['title']} | `{c_item['diagnostic_codes']}` | {c_item['vehicle_system']} |"
            )

        lines.append("")

    with open(md_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Generated comprehensive markdown evaluation report at '{md_out_path}'.")


if __name__ == "__main__":
    main()
