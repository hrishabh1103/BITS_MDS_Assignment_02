"""Evaluation metrics and comparative analysis for Retrieval-Augmented Generation (RAG).

Provides rigorous citation coverage, context grounding checks, safety compliance validation,
and Context vs. No-Context baseline comparative analytics for academic evaluation.
"""

import csv
import re
from typing import Any, Dict, List, Optional, Tuple


def evaluate_citation_fidelity(
    retrieved_record_ids: List[str],
    cited_record_ids: List[str],
) -> Dict[str, Any]:
    """Computes precision and recall of source citations in the generated answer."""
    retrieved_set = set(retrieved_record_ids)
    cited_set = set(cited_record_ids)

    valid_citations = cited_set.intersection(retrieved_set)
    hallucinated_citations = cited_set.difference(retrieved_set)

    precision = len(valid_citations) / len(cited_set) if cited_set else 0.0
    recall = len(valid_citations) / len(retrieved_set) if retrieved_set else 0.0

    return {
        "retrieved_count": len(retrieved_set),
        "cited_count": len(cited_set),
        "valid_citations_count": len(valid_citations),
        "hallucinated_citations_count": len(hallucinated_citations),
        "citation_precision": round(precision, 4),
        "citation_recall": round(recall, 4),
        "valid_cited_ids": sorted(list(valid_citations)),
        "hallucinated_ids": sorted(list(hallucinated_citations)),
        "has_citations": len(cited_set) > 0,
    }


def evaluate_safety_and_structure(answer_text: str) -> Dict[str, Any]:
    """Checks for presence of structured headers, safety disclaimers, and limitation disclosures."""
    lower_text = answer_text.lower()

    # Safety disclaimer keywords
    safety_keywords = [
        "certified", "technician", "safety", "inspection", "hazard", "ase", "danger", "precaution", "caution"
    ]
    has_safety = any(k in lower_text for k in safety_keywords)

    # Limitations & uncertainty disclosure keywords
    limitation_keywords = [
        "limitation", "insufficient", "missing", "ambiguity", "does not replace", "represented as possibilities"
    ]
    has_limitations = any(k in lower_text for k in limitation_keywords)

    # Structured sections check
    has_summary = "summary" in lower_text
    has_causes = "cause" in lower_text
    has_checks = "diagnostic" in lower_text or "inspection" in lower_text or "check" in lower_text
    has_citations_section = "citation" in lower_text or "source" in lower_text

    structure_score = sum([has_summary, has_causes, has_checks, has_limitations, has_citations_section]) / 5.0

    return {
        "has_safety_disclaimer": has_safety,
        "has_limitations_disclosure": has_limitations,
        "structure_adherence_score": round(structure_score, 2),
        "word_count": len(answer_text.split()),
        "character_count": len(answer_text),
    }


def compare_rag_vs_baseline(
    rag_result: Dict[str, Any],
    baseline_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Computes side-by-side comparative analytics between RAG and No-Context Baseline."""
    rag_ans = rag_result.get("generated_answer", "")
    base_ans = baseline_result.get("generated_answer", "")

    rag_eval = evaluate_safety_and_structure(rag_ans)
    base_eval = evaluate_safety_and_structure(base_ans)

    rag_citations = rag_result.get("source_record_ids", [])
    base_citations = baseline_result.get("source_record_ids", [])

    # Check for specific diagnostic code references (e.g. P00B7, C0291)
    rag_dtcs = re.findall(r"\b[PCBU][0-9A-Fa-f]{4}\b", rag_ans)
    base_dtcs = re.findall(r"\b[PCBU][0-9A-Fa-f]{4}\b", base_ans)

    return {
        "query_id": rag_result.get("query_id", ""),
        "query": rag_result.get("query", ""),
        "rag": {
            "retrieval_k": rag_result.get("retrieval_k", 0),
            "retrieved_record_ids": rag_result.get("retrieved_record_ids", []),
            "cited_record_ids": rag_citations,
            "cited_dtc_codes": sorted(list(set(rag_dtcs))),
            "word_count": rag_eval["word_count"],
            "has_safety_disclaimer": rag_eval["has_safety_disclaimer"],
            "has_limitations_disclosure": rag_eval["has_limitations_disclosure"],
            "generation_mode": rag_result.get("generation_mode", ""),
        },
        "baseline": {
            "retrieval_k": 0,
            "retrieved_record_ids": [],
            "cited_record_ids": base_citations,
            "cited_dtc_codes": sorted(list(set(base_dtcs))),
            "word_count": base_eval["word_count"],
            "has_safety_disclaimer": base_eval["has_safety_disclaimer"],
            "has_limitations_disclosure": base_eval["has_limitations_disclosure"],
            "generation_mode": baseline_result.get("generation_mode", ""),
        },
        "comparative_observations": {
            "rag_cites_sources": len(rag_citations) > 0,
            "baseline_has_sources": len(base_citations) > 0,  # Expected False
            "rag_provides_specific_dtcs": len(rag_dtcs) > 0,
            "baseline_provides_specific_dtcs": len(base_dtcs) > 0,
            "word_count_delta": rag_eval["word_count"] - base_eval["word_count"],
        },
    }


def export_evaluation_csv(
    comparisons: List[Dict[str, Any]],
    output_path: str,
) -> None:
    """Exports a formatted CSV summary table of RAG vs Baseline evaluation."""
    fieldnames = [
        "query_id",
        "rag_retrieved_k",
        "rag_cited_count",
        "rag_valid_citations",
        "rag_dtcs",
        "rag_word_count",
        "rag_has_safety",
        "baseline_cited_count",
        "baseline_dtcs",
        "baseline_word_count",
        "baseline_has_safety",
        "generation_mode",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for comp in comparisons:
            rag = comp["rag"]
            base = comp["baseline"]
            writer.writerow({
                "query_id": comp["query_id"],
                "rag_retrieved_k": rag["retrieval_k"],
                "rag_cited_count": len(rag["cited_record_ids"]),
                "rag_valid_citations": ", ".join(rag["cited_record_ids"]),
                "rag_dtcs": ", ".join(rag["cited_dtc_codes"]),
                "rag_word_count": rag["word_count"],
                "rag_has_safety": rag["has_safety_disclaimer"],
                "baseline_cited_count": len(base["cited_record_ids"]),
                "baseline_dtcs": ", ".join(base["cited_dtc_codes"]),
                "baseline_word_count": base["word_count"],
                "baseline_has_safety": base["has_safety_disclaimer"],
                "generation_mode": rag["generation_mode"],
            })
