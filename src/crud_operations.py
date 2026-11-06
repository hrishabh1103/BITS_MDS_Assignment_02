"""CRUD operations demonstration module for the ChromaDB Vehicle Knowledge Base.

Demonstrates isolated Create, Read, Update, and Delete operations on a
dedicated sandbox record without affecting the production dataset records.
"""

from typing import Any, Dict, Optional
from src.chroma_manager import ChromaDBManager
from src.utils import setup_logger

logger = setup_logger("crud_operations")

# Dedicated test record ID strictly reserved for CRUD demonstration
TEST_RECORD_ID = "TEST-VTR-CRUD-001"


def get_sample_test_record() -> Dict[str, Any]:
    """Generates a dedicated test record for CRUD verification."""
    return {
        "id": TEST_RECORD_ID,
        "title": "DTC TEST-P9999 - Diagnostic Sandbox Test Fault",
        "document": (
            "Title: DTC TEST-P9999 - Diagnostic Sandbox Test Fault\n"
            "Diagnostic Codes: TEST-P9999\n"
            "Vehicle System: Electrical And Body\n"
            "Problem Description: Isolated sandbox troubleshooting record created strictly for testing ChromaDB CRUD operations.\n"
            "Symptoms: Synthetic test warning indicator illuminated\n"
            "Possible Causes: Unit test harness execution (likelihood: high)\n"
            "Diagnostic Steps: 1. Confirm test record insertion. 2. Verify retrieval. 3. Update metadata. 4. Delete.\n"
            "Recommended Actions: Delete record upon completion of verification suite."
        ),
        "metadata": {
            "id": TEST_RECORD_ID,
            "title": "DTC TEST-P9999 - Diagnostic Sandbox Test Fault",
            "diagnostic_codes": "TEST-P9999",
            "vehicle_system": "electrical_and_body",
            "severity": "low",
            "vehicle_type": "passenger_car_and_light_truck",
            "source": "Academic Sandbox Harness",
            "source_url": "https://bits-wilp.ac.in",
            "source_record_id": "TEST-P9999",
            "data_origin": "crud_test_fixture",
            "symptoms": "Synthetic test warning indicator illuminated",
            "possible_causes": "Unit test harness execution",
        },
    }


def run_crud_demonstration(manager: Optional[ChromaDBManager] = None) -> Dict[str, Any]:
    """Executes a complete Create, Read, Update, Delete lifecycle test."""
    db = manager or ChromaDBManager()
    results: Dict[str, Any] = {
        "test_record_id": TEST_RECORD_ID,
        "create_success": False,
        "read_success": False,
        "update_success": False,
        "delete_success": False,
        "all_passed": False,
        "log": [],
    }

    test_rec = get_sample_test_record()

    # Clean up any leftover test record first
    try:
        db.delete_record(TEST_RECORD_ID)
    except Exception:
        pass

    initial_count = db.get_count()
    results["log"].append(f"Initial collection count: {initial_count}")

    # 1. CREATE
    logger.info(f"[CREATE] Inserting test record {TEST_RECORD_ID}...")
    db.add_records_batch(
        ids=[test_rec["id"]],
        documents=[test_rec["document"]],
        metadatas=[test_rec["metadata"]],
        batch_size=1,
    )
    post_create_count = db.get_count()
    if post_create_count == initial_count + 1:
        results["create_success"] = True
        results["log"].append(f"CREATE passed: Collection count increased from {initial_count} to {post_create_count}")
    else:
        results["log"].append(f"CREATE failed: Count did not increment as expected ({initial_count} -> {post_create_count})")

    # 2. READ
    logger.info(f"[READ] Retrieving record {TEST_RECORD_ID}...")
    fetched = db.get_record_by_id(TEST_RECORD_ID)
    if fetched and fetched["id"] == TEST_RECORD_ID and fetched["metadata"]["severity"] == "low":
        results["read_success"] = True
        results["log"].append(f"READ passed: Successfully retrieved record {TEST_RECORD_ID} with matching metadata")
    else:
        results["log"].append(f"READ failed: Fetched record mismatch or not found: {fetched}")

    # 3. UPDATE
    logger.info(f"[UPDATE] Updating metadata of record {TEST_RECORD_ID}...")
    updated_metadata = dict(test_rec["metadata"])
    updated_metadata["severity"] = "high"
    updated_metadata["update_timestamp"] = "2026-11-06T19:00:00"

    db.update_record(
        record_id=TEST_RECORD_ID,
        metadata=updated_metadata,
    )

    re_fetched = db.get_record_by_id(TEST_RECORD_ID)
    if re_fetched and re_fetched["metadata"].get("severity") == "high":
        results["update_success"] = True
        results["log"].append(f"UPDATE passed: Severity successfully updated from 'low' to 'high'")
    else:
        results["log"].append(f"UPDATE failed: Updated metadata not reflected: {re_fetched}")

    # 4. DELETE
    logger.info(f"[DELETE] Deleting record {TEST_RECORD_ID}...")
    db.delete_record(TEST_RECORD_ID)
    post_delete_count = db.get_count()
    final_fetch = db.get_record_by_id(TEST_RECORD_ID)

    if final_fetch is None and post_delete_count == initial_count:
        results["delete_success"] = True
        results["log"].append(f"DELETE passed: Record deleted and count returned to initial {post_delete_count}")
    else:
        results["log"].append(f"DELETE failed: Record still present or count mismatch ({post_delete_count} vs {initial_count})")

    results["all_passed"] = (
        results["create_success"]
        and results["read_success"]
        and results["update_success"]
        and results["delete_success"]
    )
    logger.info(f"CRUD demonstration completed. Status: {'ALL PASSED' if results['all_passed'] else 'FAILED'}")
    return results


if __name__ == "__main__":
    report = run_crud_demonstration()
    print("--- CRUD Operations Summary ---")
    for k, v in report.items():
        if k == "log":
            print("Log:")
            for entry in v:
                print(f"  * {entry}")
        else:
            print(f"{k}: {v}")
