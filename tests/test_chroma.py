"""Unit and integration tests for ChromaDB persistent storage, embeddings, CRUD, and retrieval."""

import pytest
import numpy as np
import chromadb
from pathlib import Path
from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.embeddings import EmbeddingManager, create_record_text, format_metadata_for_chroma
from src.chroma_manager import ChromaDBManager
from src.crud_operations import run_crud_demonstration, TEST_RECORD_ID
from src.semantic_search import SemanticSearchEngine


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


def test_embedding_dimensions(embedding_mgr):
    """Verify embedding model outputs 384-dimensional vectors."""
    assert embedding_mgr.dimension == 384
    vec = embedding_mgr.embed_text("Engine misfire on cylinder 1")
    assert vec.shape == (384,)
    assert isinstance(float(vec[0]), float)


def test_embedding_normalization(embedding_mgr):
    """Verify normalized embeddings have unit L2 norm."""
    vec = embedding_mgr.embed_text("Alternator charging failure", normalize=True)
    norm = float(np.linalg.norm(vec))
    assert norm == pytest.approx(1.0, abs=1e-3)


def test_chroma_collection_count(chroma_mgr):
    """Verify ChromaDB persistent collection contains the full validated dataset."""
    count = chroma_mgr.get_count()
    assert count >= 5000, f"Expected at least 5000 records, got {count}"
    assert count == 9532, f"Expected exactly 9532 records, got {count}"


def test_record_retrieval_by_id(chroma_mgr):
    """Verify specific known record retrieval by ID."""
    rec = chroma_mgr.get_record_by_id("VTR-P0100")
    assert rec is not None
    assert rec["id"] == "VTR-P0100"
    assert "P0100" in rec["metadata"]["diagnostic_codes"]
    assert rec["metadata"]["vehicle_system"] == "engine_and_transmission"


def test_database_persistence_reload(embedding_mgr):
    """Verify database persistence across client re-initialization (reloading from disk)."""
    # 1. First client session: retrieve known record
    client_1 = ChromaDBManager(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_manager=embedding_mgr,
    )
    count_1 = client_1.get_count()
    rec_1 = client_1.get_record_by_id("VTR-P0300")
    assert rec_1 is not None

    # 2. Release client reference
    del client_1

    # 3. Second client session: reopen persistence directory
    client_2 = ChromaDBManager(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_manager=embedding_mgr,
    )
    count_2 = client_2.get_count()
    rec_2 = client_2.get_record_by_id("VTR-P0300")

    # 4. Assert identical count and metadata persistence
    assert count_1 == count_2 == 9532
    assert rec_2 is not None
    assert rec_1["id"] == rec_2["id"]
    assert rec_1["metadata"] == rec_2["metadata"]
    assert rec_1["document"] == rec_2["document"]


def test_crud_operations(chroma_mgr):
    """Verify Create, Read, Update, Delete lifecycle on an isolated sandbox test record."""
    report = run_crud_demonstration(chroma_mgr)
    assert report["all_passed"] is True
    assert report["create_success"] is True
    assert report["read_success"] is True
    assert report["update_success"] is True
    assert report["delete_success"] is True
    # Ensure test record is completely cleaned up
    assert chroma_mgr.get_record_by_id(TEST_RECORD_ID) is None
    assert chroma_mgr.get_count() == 9532


def test_semantic_search_retrieval(chroma_mgr, embedding_mgr):
    """Verify semantic search returns ranked results with valid distances and metadata."""
    search_engine = SemanticSearchEngine(
        chroma_manager=chroma_mgr,
        embedding_manager=embedding_mgr,
    )
    results = search_engine.search("loss of brake hydraulic pressure", top_k=5)
    assert len(results) == 5
    assert results[0]["rank"] == 1
    assert 0.0 <= results[0]["distance"] <= 2.0
    assert 0.0 <= results[0]["similarity_score"] <= 1.0
    for r in results:
        assert r["id"].startswith("VTR-")
        assert len(r["title"]) > 0
        assert r["source_url"].startswith("http")


def test_semantic_search_with_metadata_filter(chroma_mgr, embedding_mgr):
    """Verify semantic search respects metadata filtering."""
    search_engine = SemanticSearchEngine(
        chroma_manager=chroma_mgr,
        embedding_manager=embedding_mgr,
    )
    results = search_engine.search(
        query="fault in control circuit",
        top_k=5,
        where={"vehicle_system": "brakes_and_suspension"},
    )
    assert len(results) > 0
    for r in results:
        assert r["vehicle_system"] == "brakes_and_suspension"
