"""Unit and integration tests for NumPy similarity metrics and Phase 5 evaluation.

Verifies mathematical correctness of Euclidean distance, Cosine similarity, and Dot Product
against hand-calculated values, tests edge cases (zero division, dimension mismatches, ties),
verifies monotonicity and ranking equivalence on normalized vectors, verifies ranking divergence
on synthetic unnormalized vectors, and validates end-to-end evaluation across all 10 assignment queries.
"""

import json
from pathlib import Path
import numpy as np
import pytest

from src.chroma_manager import ChromaDBManager
from src.config import EXPERIMENTS_DIR, PROCESSED_DATASET_FILE
from src.similarity_metrics import (
    compare_rankings,
    euclidean_distance,
    cosine_similarity,
    dot_product,
    rank_documents,
    run_synthetic_metric_divergence_experiment,
)


def test_euclidean_distance_hand_calculated():
    """Verifies Euclidean distance matches manual Pythagorean calculations."""
    query = np.array([0.0, 0.0], dtype=np.float64)
    docs = np.array([
        [3.0, 4.0],   # dist = sqrt(3^2 + 4^2) = 5.0
        [1.0, 1.0],   # dist = sqrt(1^2 + 1^2) = sqrt(2) ~ 1.41421356
        [0.0, 0.0],   # dist = 0.0
        [-3.0, -4.0], # dist = 5.0
    ], dtype=np.float64)

    distances = euclidean_distance(docs, query)
    assert np.isclose(distances[0], 5.0)
    assert np.isclose(distances[1], np.sqrt(2.0))
    assert np.isclose(distances[2], 0.0)
    assert np.isclose(distances[3], 5.0)


def test_cosine_similarity_hand_calculated():
    """Verifies Cosine similarity matches known trigonometric alignments."""
    query = np.array([1.0, 0.0], dtype=np.float64)
    docs = np.array([
        [1.0, 0.0],    # angle 0 deg -> cos = 1.0
        [0.0, 1.0],    # angle 90 deg -> cos = 0.0
        [-1.0, 0.0],   # angle 180 deg -> cos = -1.0
        [10.0, 0.0],   # magnitude 10x, angle 0 deg -> cos = 1.0
        [1.0, 1.0],    # angle 45 deg -> cos = 1/sqrt(2) ~ 0.70710678
    ], dtype=np.float64)

    sims = cosine_similarity(docs, query)
    assert np.isclose(sims[0], 1.0)
    assert np.isclose(sims[1], 0.0)
    assert np.isclose(sims[2], -1.0)
    assert np.isclose(sims[3], 1.0)
    assert np.isclose(sims[4], 1.0 / np.sqrt(2.0))


def test_dot_product_hand_calculated():
    """Verifies Dot Product matches manual matrix-vector multiplication."""
    query = np.array([2.0, -3.0], dtype=np.float64)
    docs = np.array([
        [4.0, 5.0],    # 2*4 + (-3)*5 = 8 - 15 = -7.0
        [-2.0, 3.0],   # 2*(-2) + (-3)*3 = -4 - 9 = -13.0
        [1.0, 0.0],    # 2*1 + (-3)*0 = 2.0
    ], dtype=np.float64)

    dots = dot_product(docs, query)
    assert np.isclose(dots[0], -7.0)
    assert np.isclose(dots[1], -13.0)
    assert np.isclose(dots[2], 2.0)


def test_zero_vector_edge_case_safety():
    """Verifies zero vectors do not cause division by zero, NaNs, or crashes."""
    zero_q = np.array([0.0, 0.0], dtype=np.float64)
    normal_q = np.array([1.0, 2.0], dtype=np.float64)
    docs = np.array([
        [0.0, 0.0],
        [3.0, 4.0],
    ], dtype=np.float64)

    # Cosine with zero query
    sim_zero_q = cosine_similarity(docs, zero_q)
    assert not np.any(np.isnan(sim_zero_q))
    assert not np.any(np.isinf(sim_zero_q))
    assert np.all(sim_zero_q == 0.0)

    # Cosine with zero doc
    sim_zero_doc = cosine_similarity(docs, normal_q)
    assert not np.any(np.isnan(sim_zero_doc))
    assert not np.any(np.isinf(sim_zero_doc))
    assert sim_zero_doc[0] == 0.0  # zero doc gets similarity 0.0


def test_dimension_mismatch_raises_error():
    """Verifies ValueError is raised if dimensions do not match."""
    docs = np.ones((5, 10))
    wrong_q = np.ones(8)

    with pytest.raises(ValueError, match="Dimension mismatch"):
        euclidean_distance(docs, wrong_q)

    with pytest.raises(ValueError, match="Dimension mismatch"):
        cosine_similarity(docs, wrong_q)

    with pytest.raises(ValueError, match="Dimension mismatch"):
        dot_product(docs, wrong_q)


def test_normalized_vectors_exact_order_preservation():
    """Verifies mathematical theorem: on unit-normalized vectors, all three metrics preserve rank order."""
    rng = np.random.default_rng(42)
    # Generate 50 random vectors of dim 64
    raw_docs = rng.standard_normal((50, 64))
    raw_query = rng.standard_normal(64)

    # Normalize to unit length
    docs_norm = raw_docs / np.linalg.norm(raw_docs, axis=1, keepdims=True)
    query_norm = raw_query / np.linalg.norm(raw_query)

    doc_ids = [f"DOC-{i:03d}" for i in range(50)]

    euc = euclidean_distance(docs_norm, query_norm)
    cos = cosine_similarity(docs_norm, query_norm)
    dot = dot_product(docs_norm, query_norm)

    top_euc = rank_documents(euc, "euclidean", doc_ids, top_k=20)
    top_cos = rank_documents(cos, "cosine", doc_ids, top_k=20)
    top_dot = rank_documents(dot, "dot_product", doc_ids, top_k=20)

    euc_ids = [x["record_id"] for x in top_euc]
    cos_ids = [x["record_id"] for x in top_cos]
    dot_ids = [x["record_id"] for x in top_dot]

    assert cos_ids == dot_ids, "Cosine and Dot Product must yield identical rankings on unit-normalized vectors"
    assert cos_ids == euc_ids, "Cosine and Euclidean Distance must yield identical rankings on unit-normalized vectors"


def test_synthetic_unnormalized_divergence():
    """Verifies that unnormalized vectors demonstrate ranking divergence as expected."""
    experiment = run_synthetic_metric_divergence_experiment()

    unnorm = experiment["unnormalized"]
    euc_top1 = unnorm["euclidean_ranking"][0]["record_id"]
    cos_top1 = unnorm["cosine_ranking"][0]["record_id"]
    dot_top1 = unnorm["dot_product_ranking"][0]["record_id"]

    # Doc_A is unit length and collinear with query [1,0] -> distance 0.0, cosine 1.0, dot 1.0
    # Doc_B is 10x length and collinear with query [1,0] -> distance 9.0, cosine 1.0, dot 10.0
    assert "Doc_A" in euc_top1, "Euclidean distance should favor small distance Doc_A"
    assert "Doc_B" in dot_top1, "Dot product should favor huge magnitude Doc_B"
    assert "Doc_A" in cos_top1 or "Doc_B" in cos_top1, "Cosine similarity handles both orientation-aligned vectors"

    # In normalized mode, all three should agree
    norm = experiment["normalized"]
    norm_euc_top1 = norm["euclidean_ranking"][0]["record_id"]
    norm_cos_top1 = norm["cosine_ranking"][0]["record_id"]
    norm_dot_top1 = norm["dot_product_ranking"][0]["record_id"]
    assert norm_euc_top1 == norm_cos_top1 == norm_dot_top1


def test_ranking_determinism_and_tie_breaking():
    """Verifies that tie-breaking on identical scores produces stable lexicographical ordering."""
    scores = np.array([0.5, 0.5, 0.8, 0.5])
    ids = ["VTR-C", "VTR-A", "VTR-Z", "VTR-B"]

    # For descending sort (cosine / dot), top 1 is VTR-Z (0.8)
    # Next three are tied at 0.5; secondary key should sort VTR-A, VTR-B, VTR-C
    ranked = rank_documents(scores, "cosine", ids, top_k=4)
    ordered_ids = [x["record_id"] for x in ranked]
    assert ordered_ids == ["VTR-Z", "VTR-A", "VTR-B", "VTR-C"]


def test_end_to_end_all_ten_queries_evaluated():
    """Validates the complete Phase 5 evaluation results artifact."""
    results_file = EXPERIMENTS_DIR / "similarity_comparison_results.json"
    assert results_file.exists(), f"Results file '{results_file}' does not exist. Run scripts/run_similarity_comparison.py first."

    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Metadata verification
    meta = data["metadata"]
    assert meta["total_queries"] == 10
    assert meta["total_documents"] == 9532
    assert meta["embedding_dimension"] == 384
    assert meta["document_embeddings_normalized"] is True
    assert meta["total_evaluations"] == 60

    # 2. Load dataset IDs to cross-verify all returned IDs
    with open(PROCESSED_DATASET_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    valid_ids = {r["id"] for r in dataset}

    queries = data["query_evaluations"]
    assert len(queries) == 10

    for q in queries:
        qid = q["query_id"]
        assert q["query_embedding_normalized"] is True

        # Check computation latencies
        latencies = q["computation_latencies_ms"]
        assert latencies["euclidean"] > 0
        assert latencies["cosine"] > 0
        assert latencies["dot_product"] > 0

        # Check K=5 and K=10 for each metric
        for m in ["euclidean", "cosine", "dot_product"]:
            r5 = q["rankings_k5"][m]
            r10 = q["rankings_k10"][m]
            assert len(r5) == 5, f"Expected 5 results for {qid} {m} K=5, got {len(r5)}"
            assert len(r10) == 10, f"Expected 10 results for {qid} {m} K=10, got {len(r10)}"

            # Verify no duplicates in top-k
            ids_5 = [x["record_id"] for x in r5]
            ids_10 = [x["record_id"] for x in r10]
            assert len(ids_5) == len(set(ids_5)), f"Duplicate IDs found in {qid} {m} K=5"
            assert len(ids_10) == len(set(ids_10)), f"Duplicate IDs found in {qid} {m} K=10"

            # Verify IDs exist in dataset
            for rec_id in ids_10:
                assert rec_id in valid_ids, f"Retrieved record ID '{rec_id}' does not exist in dataset"

        # Check metric agreement on unit-normalized embeddings
        pk5 = q["pairwise_comparisons"]["k5"]
        assert pk5["cosine_vs_dot"]["exact_order_match"] is True
        assert pk5["cosine_vs_euclidean"]["exact_order_match"] is True

        pk10 = q["pairwise_comparisons"]["k10"]
        assert pk10["cosine_vs_dot"]["exact_order_match"] is True
        assert pk10["cosine_vs_euclidean"]["exact_order_match"] is True


def test_chromadb_collection_count_strictly_preserved():
    """Verifies that Phase 5 operations were read-only and preserved all 9,532 records in ChromaDB."""
    chroma_mgr = ChromaDBManager()
    count = chroma_mgr.get_count()
    assert count == 9532, f"ChromaDB collection count modified! Expected 9532, got {count}"
