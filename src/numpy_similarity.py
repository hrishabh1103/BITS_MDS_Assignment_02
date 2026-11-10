"""Exhaustive NumPy similarity metrics implementation.

Re-exports core functions from src.similarity_metrics for backwards compatibility.
"""

from src.similarity_metrics import (
    compare_rankings,
    compute_all_metrics,
    cosine_similarity,
    dot_product,
    euclidean_distance,
    rank_documents,
    run_synthetic_metric_divergence_experiment,
)

__all__ = [
    "compare_rankings",
    "compute_all_metrics",
    "cosine_similarity",
    "dot_product",
    "euclidean_distance",
    "rank_documents",
    "run_synthetic_metric_divergence_experiment",
]

