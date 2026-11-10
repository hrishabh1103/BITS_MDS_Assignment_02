"""Evaluation utilities module.

Re-exports core functions from src.rag_evaluation for compatibility.
"""

from src.rag_evaluation import (
    compare_rag_vs_baseline,
    evaluate_citation_fidelity,
    evaluate_safety_and_structure,
    export_evaluation_csv,
)

__all__ = [
    "compare_rag_vs_baseline",
    "evaluate_citation_fidelity",
    "evaluate_safety_and_structure",
    "export_evaluation_csv",
]
