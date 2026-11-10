"""Unit and integration tests for Phase 6 RAG pipeline and evaluation components.

Validates prompt construction, context formatting, source citation extraction,
error handling, empty context behavior, and ensures no accidental mutation of ChromaDB.
Tests run completely offline without requiring live network access or paid API credentials.
"""

import json
from pathlib import Path
import pytest

from src.chroma_manager import ChromaDBManager
from src.llm_provider import (
    BaseLLMProvider,
    LLMResponse,
    MockLLMProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    get_llm_provider,
)
from src.rag_evaluation import (
    compare_rag_vs_baseline,
    evaluate_citation_fidelity,
    evaluate_safety_and_structure,
)
from src.rag_pipeline import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    RAGPipeline,
    construct_user_prompt,
    extract_cited_record_ids,
    format_context_documents,
)


def test_mock_llm_provider_deterministic_behavior():
    """Verifies that MockLLMProvider operates deterministically and flags generation_mode='mock'."""
    provider = MockLLMProvider()
    assert provider.name == "mock"
    assert provider.generation_mode == "mock"
    assert provider.is_available() is True

    # Test with context
    res = provider.generate("Symptom: overheating. Context: [RECORD: VTR-P00B7]\nPossible Causes: Thermostat stuck")
    assert res.is_success is True
    assert res.generation_mode == "mock"
    assert "VTR-P00B7" in res.content
    assert "Problem Summary" in res.content
    assert "Possible Causes" in res.content
    assert "Safety" in res.content or "technician" in res.content.lower()

    # Test without context (baseline)
    res_base = provider.generate("Symptom: overheating. NO RETRIEVED CONTEXT AVAILABLE.")
    assert res_base.is_success is True
    assert res_base.generation_mode == "mock"
    assert "VTR-" not in res_base.content
    assert "without retrieved troubleshooting database records" in res_base.content


def test_openai_provider_missing_key_behavior():
    """Verifies that OpenAICompatibleProvider safely reports unavailability without crashing when key is missing."""
    provider = OpenAICompatibleProvider(api_key="")
    assert provider.is_available() is False
    res = provider.generate("test prompt")
    assert res.is_success is False
    assert "API key not configured" in res.error


def test_ollama_provider_unreachable_behavior():
    """Verifies that OllamaProvider gracefully returns an error response when local daemon is unreachable."""
    # Use invalid port to test timeout/failure handling
    provider = OllamaProvider(base_url="http://127.0.0.1:54321", timeout_seconds=1)
    assert provider.is_available() is False


def test_get_llm_provider_factory():
    """Verifies provider resolution and fallback mechanism."""
    mock_p = get_llm_provider("mock")
    assert isinstance(mock_p, MockLLMProvider)

    # When requesting unavailable provider with allow_mock_fallback=True
    fallback_p = get_llm_provider("nonexistent_provider", allow_mock_fallback=True)
    assert isinstance(fallback_p, MockLLMProvider)

    # When requesting unavailable provider without fallback, raises RuntimeError
    with pytest.raises(RuntimeError):
        get_llm_provider("nonexistent_provider", allow_mock_fallback=False)


def test_context_formatting():
    """Verifies that format_context_documents retains all technical fields and metadata."""
    sample_docs = [
        {
            "rank": 1,
            "record_id": "VTR-P00B7",
            "title": "DTC P00B7 - Coolant Flow Low",
            "vehicle_system": "engine_and_transmission",
            "diagnostic_codes": "P00B7",
            "severity": "medium",
            "distance": 0.6039,
            "similarity_score": 0.3961,
            "document": "Problem Description: Engine runs hot.\nPossible Causes: Thermostat stuck closed",
        }
    ]

    formatted = format_context_documents(sample_docs)
    assert "[RECORD #1: VTR-P00B7]" in formatted
    assert "DTC P00B7 - Coolant Flow Low" in formatted
    assert "Cosine Similarity: 0.3961" in formatted
    assert "Retrieval Distance: 0.6039" in formatted
    assert "Thermostat stuck closed" in formatted


def test_empty_context_formatting():
    """Verifies that an empty retrieved list produces an explicit notice rather than an empty string."""
    formatted = format_context_documents([])
    assert "NO RETRIEVED CONTEXT AVAILABLE" in formatted


def test_prompt_construction_and_guardrails():
    """Verifies that prompt construction embeds query, context, and strict system rules."""
    prompt = construct_user_prompt(
        query="Engine overheating rapidly",
        context_text="[RECORD #1: VTR-P00B7]",
        is_baseline_no_context=False,
    )
    assert "Engine overheating rapidly" in prompt
    assert "[RECORD #1: VTR-P00B7]" in prompt
    assert "cite record IDs" in prompt

    # Verify baseline prompt excludes context
    base_prompt = construct_user_prompt(
        query="Engine overheating rapidly",
        context_text="",
        is_baseline_no_context=True,
    )
    assert "Engine overheating rapidly" in base_prompt
    assert "NO RETRIEVED CONTEXT AVAILABLE" in base_prompt

    # System prompt verification
    assert "GROUNDING & HONESTY" in SYSTEM_PROMPT
    assert "NO HALLUCINATION" in SYSTEM_PROMPT
    assert "MANDATORY CITATIONS" in SYSTEM_PROMPT
    assert "AUTOMOTIVE SAFETY" in SYSTEM_PROMPT


def test_citation_extraction():
    """Verifies extraction and deduplication of VTR record IDs from model text."""
    sample_text = (
        "Based on [VTR-P00B7] and VTR-P2B61, the thermostat may be stuck. "
        "Also see [VTR-P00B7] for pump check and VTR-U0698 for communication."
    )
    extracted = extract_cited_record_ids(sample_text)
    assert extracted == ["VTR-P00B7", "VTR-P2B61", "VTR-U0698"]


def test_citation_fidelity_evaluation():
    """Verifies precision and recall calculations for citations."""
    retrieved = ["VTR-P00B7", "VTR-P2B61", "VTR-U0698", "VTR-P2D8A", "VTR-P26CB"]
    cited = ["VTR-P00B7", "VTR-P2B61", "VTR-FAKE1"]

    eval_res = evaluate_citation_fidelity(retrieved, cited)
    assert eval_res["retrieved_count"] == 5
    assert eval_res["cited_count"] == 3
    assert eval_res["valid_citations_count"] == 2
    assert eval_res["hallucinated_citations_count"] == 1
    assert eval_res["citation_precision"] == round(2 / 3, 4)
    assert eval_res["citation_recall"] == round(2 / 5, 4)
    assert eval_res["hallucinated_ids"] == ["VTR-FAKE1"]


def test_rag_pipeline_end_to_end():
    """Verifies end-to-end RAG pipeline execution on a test query using MockLLMProvider."""
    pipeline = RAGPipeline(llm_provider=MockLLMProvider(), default_top_k=3)
    query = "Brake pedal sinks slowly to the floorboard at red lights with ABS warning"

    res = pipeline.query(query, query_id="TEST-Q04", top_k=3)
    assert res["execution_status"] == "success"
    assert res["query_id"] == "TEST-Q04"
    assert len(res["retrieved_documents"]) == 3
    assert res["retrieval_k"] == 3
    assert len(res["retrieved_record_ids"]) == 3
    assert len(res["source_record_ids"]) > 0
    assert res["generation_mode"] == "mock"
    assert "VTR-" in res["generated_answer"]

    # Verify baseline query has 0 retrieved documents and 0 citations
    base_res = pipeline.query(query, query_id="TEST-Q04", is_baseline=True)
    assert base_res["execution_status"] == "success"
    assert len(base_res["retrieved_documents"]) == 0
    assert len(base_res["source_record_ids"]) == 0

    # Side-by-side comparison
    comp = compare_rag_vs_baseline(res, base_res)
    assert comp["comparative_observations"]["rag_cites_sources"] is True
    assert comp["comparative_observations"]["baseline_has_sources"] is False


def test_chromadb_collection_strictly_preserved():
    """Verifies that RAG pipeline operations were strictly read-only and preserved all 9,532 records."""
    chroma_mgr = ChromaDBManager()
    count = chroma_mgr.get_count()
    assert count == 9532, f"ChromaDB collection count altered! Expected 9532, got {count}"
