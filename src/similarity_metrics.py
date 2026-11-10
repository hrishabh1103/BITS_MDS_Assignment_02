"""NumPy similarity and distance metrics for vector comparison.

Implements pure NumPy formulations for Euclidean distance (L2), Cosine similarity,
and Dot Product. Provides robust sorting, deterministic tie-breaking, rank comparison
analytics, and synthetic demonstration of unnormalized metric divergence.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from src.utils import setup_logger

logger = setup_logger("similarity_metrics")


def euclidean_distance(
    documents: np.ndarray,
    query: np.ndarray,
) -> np.ndarray:
    """Computes Euclidean (L2) distance between a matrix of document embeddings and a query.

    Mathematical formulation:
        d_L2(x_i, q) = ||x_i - q||_2 = sqrt(sum_{j=1}^D (x_{i,j} - q_j)^2)

    Args:
        documents: 2D array of shape (N, D) representing document embeddings.
        query: 1D array of shape (D,) representing the query embedding.

    Returns:
        1D array of shape (N,) containing non-negative Euclidean distances.
        Smaller distance indicates higher semantic proximity.
    """
    if documents.ndim != 2:
        raise ValueError(f"documents must be a 2D array of shape (N, D), got shape {documents.shape}")
    if query.ndim == 2:
        if query.shape[0] == 1:
            query = query.reshape(-1)
        else:
            raise ValueError(f"query must be 1D or (1, D), got shape {query.shape}")
    if query.ndim != 1:
        raise ValueError(f"query must be 1D array of shape (D,), got shape {query.shape}")
    if documents.shape[1] != query.shape[0]:
        raise ValueError(f"Dimension mismatch: documents have {documents.shape[1]} dims, query has {query.shape[0]} dims")

    # Vectorized L2 norm along axis 1
    diff = documents - query
    distances = np.linalg.norm(diff, axis=1)
    return distances.astype(np.float64)


def cosine_similarity(
    documents: np.ndarray,
    query: np.ndarray,
    eps: float = 1e-12,
) -> np.ndarray:
    """Computes Cosine similarity between a matrix of document embeddings and a query.

    Mathematical formulation:
        cos(x_i, q) = (x_i . q) / (||x_i||_2 * ||q||_2)

    Handles zero-vector edge cases safely without division by zero or NaN values.
    Results are clipped to [-1.0, 1.0] to guard against numerical float imprecision.

    Args:
        documents: 2D array of shape (N, D) representing document embeddings.
        query: 1D array of shape (D,) representing the query embedding.
        eps: Small epsilon constant to prevent division by zero.

    Returns:
        1D array of shape (N,) containing cosine similarity scores in [-1.0, 1.0].
        Larger value indicates higher angular similarity.
    """
    if documents.ndim != 2:
        raise ValueError(f"documents must be a 2D array of shape (N, D), got shape {documents.shape}")
    if query.ndim == 2:
        if query.shape[0] == 1:
            query = query.reshape(-1)
        else:
            raise ValueError(f"query must be 1D or (1, D), got shape {query.shape}")
    if query.ndim != 1:
        raise ValueError(f"query must be 1D array of shape (D,), got shape {query.shape}")
    if documents.shape[1] != query.shape[0]:
        raise ValueError(f"Dimension mismatch: documents have {documents.shape[1]} dims, query has {query.shape[0]} dims")

    # Dot products: shape (N,)
    dot_products = documents @ query

    # Magnitudes (L2 norms)
    doc_norms = np.linalg.norm(documents, axis=1)
    query_norm = float(np.linalg.norm(query))

    # Safe denominator with epsilon protection
    denominator = doc_norms * query_norm
    denominator = np.where(denominator < eps, eps, denominator)

    # Compute similarity and clip to valid mathematical range
    similarity = dot_products / denominator
    similarity = np.clip(similarity, -1.0, 1.0)

    # Zero vector handling: if query or doc is zero, return 0.0
    zero_doc_mask = doc_norms < eps
    if query_norm < eps:
        similarity = np.zeros_like(similarity)
    elif np.any(zero_doc_mask):
        similarity[zero_doc_mask] = 0.0

    return similarity.astype(np.float64)


def dot_product(
    documents: np.ndarray,
    query: np.ndarray,
) -> np.ndarray:
    """Computes Dot Product (inner product) between document embeddings and a query.

    Mathematical formulation:
        x_i . q = sum_{j=1}^D (x_{i,j} * q_j)

    When both documents and query vectors are L2-normalized (unit length), the dot
    product is mathematically identical to cosine similarity. When unnormalized,
    dot product is heavily influenced by vector magnitudes.

    Args:
        documents: 2D array of shape (N, D) representing document embeddings.
        query: 1D array of shape (D,) representing the query embedding.

    Returns:
        1D array of shape (N,) containing scalar dot products.
        Larger value indicates higher inner-product score.
    """
    if documents.ndim != 2:
        raise ValueError(f"documents must be a 2D array of shape (N, D), got shape {documents.shape}")
    if query.ndim == 2:
        if query.shape[0] == 1:
            query = query.reshape(-1)
        else:
            raise ValueError(f"query must be 1D or (1, D), got shape {query.shape}")
    if query.ndim != 1:
        raise ValueError(f"query must be 1D array of shape (D,), got shape {query.shape}")
    if documents.shape[1] != query.shape[0]:
        raise ValueError(f"Dimension mismatch: documents have {documents.shape[1]} dims, query has {query.shape[0]} dims")

    scores = documents @ query
    return scores.astype(np.float64)


def rank_documents(
    scores: np.ndarray,
    metric: str,
    record_ids: List[str],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """Ranks document scores and returns the top-K records with deterministic tie-breaking.

    Args:
        scores: 1D array of shape (N,) containing metric scores.
        metric: Metric identifier ('euclidean', 'l2', 'cosine', 'dot_product', 'ip').
        record_ids: List of record ID strings corresponding to the rows of scores.
        top_k: Number of top records to retrieve.

    Returns:
        List of dicts formatted with rank, record_id, score, and original document index.
    """
    if len(scores) != len(record_ids):
        raise ValueError(f"Length mismatch: {len(scores)} scores but {len(record_ids)} record_ids")
    if top_k <= 0:
        raise ValueError(f"top_k must be a positive integer, got {top_k}")

    metric_lower = metric.lower()
    is_ascending = metric_lower in ("euclidean", "l2")

    n = len(scores)
    actual_k = min(top_k, n)

    # To guarantee completely deterministic sorting even with floating-point ties:
    # Sort key tuple: (primary_score, record_id)
    # For ascending: smallest score first.
    # For descending: largest score first (negate score or sort reverse).
    indices = np.arange(n)

    # Python sort with secondary tie-break key
    if is_ascending:
        sorted_indices = sorted(indices, key=lambda idx: (scores[idx], record_ids[idx]))
    else:
        sorted_indices = sorted(indices, key=lambda idx: (-scores[idx], record_ids[idx]))

    top_indices = sorted_indices[:actual_k]

    rankings: List[Dict[str, Any]] = []
    for rank_idx, idx in enumerate(top_indices):
        rankings.append({
            "rank": rank_idx + 1,
            "record_id": record_ids[idx],
            "score": float(scores[idx]),
            "index": int(idx),
            "metric": metric_lower,
        })

    return rankings


def compute_all_metrics(
    documents: np.ndarray,
    query: np.ndarray,
    record_ids: List[str],
    top_k: int = 10,
) -> Dict[str, List[Dict[str, Any]]]:
    """Computes Euclidean, Cosine, and Dot Product metrics and ranks top-K records for each.

    Returns:
        Dict mapping metric name ('euclidean', 'cosine', 'dot_product') to ranked results.
    """
    euc_scores = euclidean_distance(documents, query)
    cos_scores = cosine_similarity(documents, query)
    dot_scores = dot_product(documents, query)

    return {
        "euclidean": rank_documents(euc_scores, "euclidean", record_ids, top_k=top_k),
        "cosine": rank_documents(cos_scores, "cosine", record_ids, top_k=top_k),
        "dot_product": rank_documents(dot_scores, "dot_product", record_ids, top_k=top_k),
    }


def compare_rankings(
    rankings_a: List[str],
    rankings_b: List[str],
) -> Dict[str, Any]:
    """Compares two ordered lists of record IDs for overlap and exact sequence ordering.

    Returns:
        Dict with jaccard_similarity, exact_order_match, overlap_count, and total_k.
    """
    set_a = set(rankings_a)
    set_b = set(rankings_b)

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)

    jaccard = len(intersection) / len(union) if union else 1.0
    exact_order = rankings_a == rankings_b

    return {
        "jaccard_similarity": round(jaccard, 4),
        "exact_order_match": exact_order,
        "overlap_count": len(intersection),
        "total_k": len(rankings_a),
    }


def run_synthetic_metric_divergence_experiment() -> Dict[str, Any]:
    """Demonstrates mathematical divergence of Euclidean, Cosine, and Dot Product on unnormalized vectors.

    Creates controlled synthetic 2D vectors where direction and magnitude diverge:
        Query q: [1.0, 0.0]
        Doc A (collinear, unit): [1.0, 0.0]  (norm=1, angle=0)
        Doc B (collinear, huge): [10.0, 0.0] (norm=10, angle=0)
        Doc C (close angle, small): [0.9, 0.2] (norm=0.92, angle=12.5 deg)
        Doc D (orthogonal, huge): [0.0, 10.0] (norm=10, angle=90 deg)

    On unit-normalized vectors, Doc A and Doc B have identical representations.
    On unnormalized vectors:
        - Cosine similarity: Doc A and Doc B both tie for #1 (cos = 1.000).
        - Dot product: Doc B heavily dominates (#1: 10.0 vs #2: 1.0) because of magnitude.
        - Euclidean distance: Doc A is closest (#1: dist = 0.0), Doc B is far (#3: dist = 9.0).

    Returns:
        Structured dictionary detailing the vectors, scores, and rankings.
    """
    query = np.array([1.0, 0.0], dtype=np.float64)
    docs = np.array([
        [1.0, 0.0],   # Doc_A: identical direction, unit length
        [10.0, 0.0],  # Doc_B: identical direction, huge magnitude (10x)
        [0.9, 0.2],   # Doc_C: slight angle (~12.5 deg), near-unit length
        [0.0, 10.0],  # Doc_D: orthogonal, huge magnitude (10x)
    ], dtype=np.float64)

    doc_ids = ["Doc_A (unit, collinear)", "Doc_B (huge, collinear)", "Doc_C (small, angled)", "Doc_D (huge, orthogonal)"]

    euc = euclidean_distance(docs, query)
    cos = cosine_similarity(docs, query)
    dot = dot_product(docs, query)

    euc_ranked = rank_documents(euc, "euclidean", doc_ids, top_k=4)
    cos_ranked = rank_documents(cos, "cosine", doc_ids, top_k=4)
    dot_ranked = rank_documents(dot, "dot_product", doc_ids, top_k=4)

    # Now compute on normalized versions of docs and query
    docs_norm = docs / np.linalg.norm(docs, axis=1, keepdims=True)
    query_norm = query / np.linalg.norm(query)

    norm_euc = euclidean_distance(docs_norm, query_norm)
    norm_cos = cosine_similarity(docs_norm, query_norm)
    norm_dot = dot_product(docs_norm, query_norm)

    norm_euc_ranked = rank_documents(norm_euc, "euclidean", doc_ids, top_k=4)
    norm_cos_ranked = rank_documents(norm_cos, "cosine", doc_ids, top_k=4)
    norm_dot_ranked = rank_documents(norm_dot, "dot_product", doc_ids, top_k=4)

    return {
        "description": "Synthetic demonstration comparing metrics on unnormalized vs normalized vectors",
        "unnormalized": {
            "query": query.tolist(),
            "documents": {doc_ids[i]: docs[i].tolist() for i in range(len(doc_ids))},
            "euclidean_ranking": euc_ranked,
            "cosine_ranking": cos_ranked,
            "dot_product_ranking": dot_ranked,
        },
        "normalized": {
            "query": query_norm.tolist(),
            "documents": {doc_ids[i]: docs_norm[i].tolist() for i in range(len(doc_ids))},
            "euclidean_ranking": norm_euc_ranked,
            "cosine_ranking": norm_cos_ranked,
            "dot_product_ranking": norm_dot_ranked,
        },
    }

