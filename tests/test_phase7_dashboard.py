"""Unit and integration tests for Phase 7 Streamlit dashboard components and views."""

import json
from pathlib import Path
import py_compile
import pytest

from src.ui.about_page import load_dataset_summary
from src.ui.assistant_page import load_preset_queries
from src.ui.components import (
    get_cached_chroma_manager,
    get_cached_rag_pipeline,
    get_cached_search_engine,
)
from src.ui.evaluation_page import (
    load_numpy_similarity_data,
    load_real_evaluation_data,
    load_semantic_search_data,
)


def test_app_py_syntax_and_compilation():
    """Verifies that app.py compiles cleanly without syntax errors."""
    compiled = py_compile.compile("app.py")
    assert compiled is not None


def test_ui_components_compilation():
    """Verifies all page modules compile cleanly without syntax errors."""
    for page in ("components", "home_page", "assistant_page", "search_page", "evaluation_page", "about_page"):
        compiled = py_compile.compile(f"src/ui/{page}.py")
        assert compiled is not None


def test_cached_chroma_manager():
    """Verifies cached ChromaDB manager loads persistent database with 9,532 records."""
    manager = get_cached_chroma_manager()
    count = manager.get_count()
    assert count == 9532, f"ChromaDB collection count mismatch! Expected 9532, got {count}"


def test_cached_search_engine():
    """Verifies cached semantic search engine retrieves top-K results correctly."""
    engine = get_cached_search_engine()
    results = engine.search(query="alternator charging voltage normal battery dead", top_k=5)
    assert len(results) == 5
    assert all("record_id" in r for r in results)
    assert all("distance" in r for r in results)


def test_cached_rag_pipeline_end_to_end():
    """Verifies cached RAG pipeline executes diagnostic query with citations and safety alerts."""
    pipeline = get_cached_rag_pipeline(provider_name="mock")
    res = pipeline.query(
        query_text="Brake pedal sinks slowly to the floorboard at red lights",
        top_k=3,
        vehicle_type="ICE",
    )
    assert res["execution_status"] in ("success", "truncated")
    assert len(res["retrieved_documents"]) == 3
    assert len(res["source_record_ids"]) > 0
    assert len(res["safety_alerts"]) > 0
    assert any(a["category"] == "BRAKING_HAZARD" for a in res["safety_alerts"])


def test_preset_queries_loading():
    """Verifies that preset assignment queries load properly."""
    presets = load_preset_queries()
    assert len(presets) >= 5
    assert any("Q01" in k for k in presets.keys())
    assert any("Q04" in k for k in presets.keys())


def test_evaluation_data_loaders():
    """Verifies that evaluation data files load seamlessly for Page 4."""
    df, real_results, comps = load_real_evaluation_data()
    assert not df.empty
    assert len(df) == 10
    assert len(comps) == 10

    sim_data = load_numpy_similarity_data()
    assert "metric_latency_summary" in sim_data

    search_data = load_semantic_search_data()
    assert "queries" in search_data


def test_about_dataset_summary_loader():
    """Verifies dataset distribution summary loader for Page 5."""
    total, systems, severities = load_dataset_summary()
    assert total == 9532
    assert "engine_and_transmission" in systems
    assert "high" in severities
