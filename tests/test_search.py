"""Unit and integration tests for semantic search, top-K retrieval, and metadata filtering."""

from pathlib import Path
import pytest
from src.chroma_manager import ChromaDBManager
from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR, QUERIES_FILE
from src.dataset_loader import load_processed_dataset
from src.embeddings import EmbeddingManager
from src.metadata_filters import (
    ASSIGNMENT_FILTER_PRESETS,
    VALID_METADATA_FIELDS,
    MetadataFilterBuilder,
)
from src.semantic_search import SemanticSearchEngine
from src.utils import load_json


@pytest.fixture(scope="module")
def dataset_records():
    """Module-level fixture to load dataset records."""
    return load_processed_dataset()


@pytest.fixture(scope="module")
def dataset_id_set(dataset_records):
    """Set of all valid dataset IDs."""
    return {r["id"] for r in dataset_records}


@pytest.fixture(scope="module")
def embedding_mgr():
    """Module-level fixture for embedding manager."""
    return EmbeddingManager()


@pytest.fixture(scope="module")
def chroma_mgr(embedding_mgr):
    """Module-level fixture for persistent ChromaDB manager."""
    return ChromaDBManager(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_manager=embedding_mgr,
    )


@pytest.fixture(scope="module")
def search_engine(chroma_mgr, embedding_mgr):
    """Module-level fixture for semantic search engine."""
    return SemanticSearchEngine(
        chroma_manager=chroma_mgr,
        embedding_manager=embedding_mgr,
    )


@pytest.fixture(scope="module")
def assignment_queries():
    """Loads the 10 assignment queries."""
    assert QUERIES_FILE.exists(), f"Queries file missing: {QUERIES_FILE}"
    queries = load_json(QUERIES_FILE)
    return queries


def test_initial_collection_count(chroma_mgr):
    """1. Verify collection count is exactly 9,532 before tests."""
    assert chroma_mgr.get_count() == 9532


def test_queries_loading_and_schema(assignment_queries):
    """2. Verify all 10 queries load correctly with mandatory fields."""
    assert len(assignment_queries) == 10
    expected_ids = [f"Q{i:02d}" for i in range(1, 11)]
    actual_ids = [q["query_id"] for q in assignment_queries]
    assert actual_ids == expected_ids

    for q in assignment_queries:
        assert len(q["query_text"].strip()) >= 20, f"Query {q['query_id']} text too short."
        assert "topic" in q and len(q["topic"]) > 0
        assert "subsystem" in q and len(q["subsystem"]) > 0
        assert "brief_rationale" in q and len(q["brief_rationale"]) > 0


def test_search_returns_results(search_engine, assignment_queries):
    """3. Verify search returns non-empty results for supported queries."""
    sample_query = assignment_queries[0]["query_text"]
    results = search_engine.search(sample_query, top_k=5)
    assert len(results) > 0
    assert results[0]["id"].startswith("VTR-")


def test_top_k_cardinality_k5(search_engine, assignment_queries):
    """4. Verify K=5 returns exactly 5 results."""
    for q in assignment_queries:
        results = search_engine.search(q["query_text"], top_k=5, query_id=q["query_id"])
        assert len(results) == 5, f"Expected 5 results for {q['query_id']}, got {len(results)}"


def test_top_k_cardinality_k10(search_engine, assignment_queries):
    """5. Verify K=10 returns exactly 10 results."""
    for q in assignment_queries[:3]:  # test across sample of queries
        results = search_engine.search(q["query_text"], top_k=10, query_id=q["query_id"])
        assert len(results) == 10, f"Expected 10 results for {q['query_id']}, got {len(results)}"


def test_distance_ordering_and_no_duplicates(search_engine, assignment_queries):
    """6. Verify ranking is ordered ascending by ChromaDB distance without duplicate IDs."""
    for q in assignment_queries:
        results = search_engine.search(q["query_text"], top_k=5, query_id=q["query_id"])
        distances = [r["distance"] for r in results]
        assert distances == sorted(distances), f"Distances not sorted ascending in {q['query_id']}: {distances}"
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids)), f"Duplicate IDs detected in {q['query_id']}: {ids}"


def test_returned_ids_exist_in_dataset(search_engine, assignment_queries, dataset_id_set):
    """7. Verify returned IDs actually exist in the indexed dataset."""
    for q in assignment_queries:
        results = search_engine.search(q["query_text"], top_k=5, query_id=q["query_id"])
        for r in results:
            assert r["id"] in dataset_id_set, f"Unknown ID {r['id']} returned for {q['query_id']}"


def test_metadata_filter_field_validation():
    """8. Verify metadata filter builder validates fields and rejects invalid ones."""
    # Valid equality
    f_valid = MetadataFilterBuilder.equals("vehicle_system", "brakes_and_suspension")
    assert f_valid == {"vehicle_system": {"$eq": "brakes_and_suspension"}}

    # Invalid field name
    with pytest.raises(ValueError, match="Invalid metadata field"):
        MetadataFilterBuilder.equals("non_existent_field", "value")

    # Invalid value for enumerated field
    with pytest.raises(ValueError, match="Invalid value"):
        MetadataFilterBuilder.equals("severity", "ultra_critical")


def test_filtered_results_satisfy_conditions(search_engine):
    """9. Verify filtered results strictly satisfy all multi-condition constraints."""
    for preset in ASSIGNMENT_FILTER_PRESETS:
        fcond = preset["filter"]
        results = search_engine.search(
            query=preset["query_text"],
            top_k=5,
            where=fcond,
        )
        assert len(results) > 0, f"Filter {preset['filter_id']} returned 0 records."
        for r in results:
            meta = r["metadata"]
            if "$and" in fcond:
                for cond in fcond["$and"]:
                    for field, op_dict in cond.items():
                        expected = op_dict["$eq"]
                        actual = meta.get(field)
                        assert actual == expected, (
                            f"Filter violation in {r['id']}: field '{field}' expected '{expected}', got '{actual}'"
                        )


def test_result_structure_completeness(search_engine, assignment_queries):
    """10. Verify result records include all necessary fields and content."""
    res = search_engine.search(assignment_queries[0]["query_text"], top_k=3, query_id="Q01")
    for r in res:
        assert "rank" in r and r["rank"] >= 1
        assert "id" in r and r["id"].startswith("VTR-")
        assert "distance" in r and 0.0 <= r["distance"] <= 2.0
        assert "similarity_score" in r and 0.0 <= r["similarity_score"] <= 1.0
        assert "title" in r and len(r["title"]) > 0
        assert "excerpt" in r and len(r["excerpt"]) > 0
        assert "document" in r and len(r["document"]) > 0
        assert "metadata" in r and isinstance(r["metadata"], dict)
        assert "source" in r and len(r["source"]) > 0
        assert "source_url" in r and r["source_url"].startswith("http")


def test_collection_remains_intact_post_experiments(chroma_mgr):
    """11 & 12. Verify search operations are read-only and collection count remains 9,532."""
    assert chroma_mgr.get_count() == 9532
