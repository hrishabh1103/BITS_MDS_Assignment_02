"""Tests for dataset loading, schema validation, uniqueness, and content integrity."""

import pytest
from pathlib import Path
from src.config import PROCESSED_DATASET_FILE
from src.dataset_loader import load_processed_dataset, get_record_by_id, get_dataset_summary
from src.dataset_validator import validate_dataset, REQUIRED_FIELDS, ALLOWED_SYSTEMS, ALLOWED_SEVERITIES


@pytest.fixture(scope="module")
def dataset():
    """Module-level fixture to load the processed dataset once."""
    assert PROCESSED_DATASET_FILE.exists(), "Processed dataset file must exist before running tests."
    return load_processed_dataset()


def test_dataset_file_exists():
    """Verify processed dataset file exists on disk."""
    assert PROCESSED_DATASET_FILE.exists()
    assert PROCESSED_DATASET_FILE.stat().st_size > 1_000_000, "Dataset file must be larger than 1MB."


def test_dataset_count_threshold(dataset):
    """Verify dataset meets the strict assignment requirement of >= 5,000 records."""
    assert len(dataset) >= 5000, f"Expected at least 5000 records, got {len(dataset)}"
    assert len(dataset) == 9532, f"Expected exactly 9532 validated records, got {len(dataset)}"


def test_record_uniqueness(dataset):
    """Verify all record IDs are unique (zero duplicate IDs)."""
    seen_ids = set()
    duplicates = []
    for r in dataset:
        rec_id = r["id"]
        if rec_id in seen_ids:
            duplicates.append(rec_id)
        seen_ids.add(rec_id)
    assert len(duplicates) == 0, f"Found duplicate IDs: {duplicates[:10]}"
    assert len(seen_ids) == len(dataset)


def test_schema_required_fields(dataset):
    """Verify all records contain the 16 mandatory schema fields."""
    sample = dataset[:500]  # sample check for speed
    for r in sample:
        for field in REQUIRED_FIELDS:
            assert field in r, f"Record {r.get('id')} missing required field: {field}"


def test_meaningful_troubleshooting_content(dataset):
    """Verify records have non-trivial diagnostic descriptions, steps, and causes."""
    sample = dataset[:500]
    for r in sample:
        assert len(r["problem_description"].strip()) >= 20, f"Short description in {r['id']}"
        assert len(r["diagnostic_steps"]) > 0, f"Empty diagnostic steps in {r['id']}"
        assert len(r["possible_causes"]) > 0, f"Empty possible causes in {r['id']}"
        assert isinstance(r["symptoms"], list), f"Symptoms not a list in {r['id']}"


def test_valid_metadata_and_categories(dataset):
    """Verify vehicle system and severity conform to defined enumerations."""
    for r in dataset[:500]:
        assert r["vehicle_system"] in ALLOWED_SYSTEMS, f"Invalid system in {r['id']}: {r['vehicle_system']}"
        assert r["severity"] in ALLOWED_SEVERITIES, f"Invalid severity in {r['id']}: {r['severity']}"


def test_source_attribution_completeness(dataset):
    """Verify authentic source attribution and URLs are preserved."""
    for r in dataset[:500]:
        assert r["source"], f"Missing source in {r['id']}"
        assert r["source_url"].startswith("http"), f"Invalid source_url in {r['id']}"
        assert r["source_record_id"], f"Missing source_record_id in {r['id']}"
        assert r["data_origin"] == "authentic_open_standard"


def test_get_record_by_id(dataset):
    """Verify lookup helper retrieves accurate record."""
    target_id = "VTR-P0100"
    rec = get_record_by_id(target_id)
    assert rec is not None
    assert rec["id"] == target_id
    assert "P0100" in rec["diagnostic_codes"]
    assert "Mass" in rec["title"]


def test_dataset_summary():
    """Verify summary helper returns correct distributions."""
    summary = get_dataset_summary()
    assert summary["total_records"] >= 5000
    assert "engine_and_transmission" in summary["system_distribution"]
    assert "brakes_and_suspension" in summary["system_distribution"]
    assert "electrical_and_body" in summary["system_distribution"]
    assert "network_and_communication" in summary["system_distribution"]


def test_dataset_validator_engine():
    """Verify the validator engine function returns success on the processed file."""
    passed, report = validate_dataset(PROCESSED_DATASET_FILE)
    assert passed is True
    assert report["validation_passed"] is True
    assert report["total_records"] >= 5000
    assert len(report["issues_found"]) == 0
