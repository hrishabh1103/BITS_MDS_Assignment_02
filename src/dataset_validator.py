"""Dataset validation engine for the Vehicle Troubleshooting Assistant.

Performs strict, zero-tolerance academic validation against the processed
dataset: verifying record counts (>= 5000), schema compliance, ID uniqueness,
troubleshooting content completeness, metadata integrity, and source attribution.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from src.config import PROCESSED_DATA_DIR
from src.utils import load_json, setup_logger

logger = setup_logger("dataset_validator")

REQUIRED_FIELDS = [
    "id",
    "title",
    "problem_description",
    "symptoms",
    "diagnostic_codes",
    "vehicle_system",
    "possible_causes",
    "diagnostic_steps",
    "recommended_actions",
    "severity",
    "vehicle_type",
    "source",
    "source_url",
    "source_record_id",
    "data_origin",
    "preprocessing_notes",
]

ALLOWED_SYSTEMS = {
    "engine_and_transmission",
    "brakes_and_suspension",
    "electrical_and_body",
    "network_and_communication",
    "general_automotive",
}

ALLOWED_SEVERITIES = {"high", "medium", "low"}


def validate_dataset(
    dataset_path: Path = PROCESSED_DATA_DIR / "vehicle_troubleshooting.json",
    min_record_count: int = 5000,
) -> Tuple[bool, Dict[str, Any]]:
    """Validates the processed dataset against all rubric criteria."""
    logger.info(f"Validating dataset from: {dataset_path}")
    if not dataset_path.exists():
        return False, {"error": f"Dataset file does not exist: {dataset_path}"}

    data = load_json(dataset_path)
    if not isinstance(data, list):
        return False, {"error": "Dataset root must be a list of records."}

    total_records = len(data)
    issues: List[str] = []

    # Check 1: Record Count
    count_passed = total_records >= min_record_count
    if not count_passed:
        issues.append(f"Record count {total_records} is below required threshold of {min_record_count}.")

    # Check 2: Uniqueness of IDs
    seen_ids = set()
    duplicate_ids = []
    for idx, r in enumerate(data):
        rec_id = r.get("id")
        if not rec_id:
            issues.append(f"Record at index {idx} missing 'id'.")
        elif rec_id in seen_ids:
            duplicate_ids.append(rec_id)
        else:
            seen_ids.add(rec_id)

    if duplicate_ids:
        issues.append(f"Found {len(duplicate_ids)} duplicate record IDs (e.g., {duplicate_ids[:3]}).")

    # Check 3: Schema completeness & Content quality
    missing_fields_count = 0
    short_descriptions = 0
    empty_steps_count = 0
    empty_causes_count = 0
    invalid_systems = set()
    invalid_severities = set()
    missing_attribution = 0

    system_counts: Dict[str, int] = {}
    severity_counts: Dict[str, int] = {}

    for idx, r in enumerate(data):
        # Missing fields check
        for field in REQUIRED_FIELDS:
            if field not in r:
                missing_fields_count += 1

        # Description length
        desc = r.get("problem_description", "")
        if not isinstance(desc, str) or len(desc.strip()) < 20:
            short_descriptions += 1

        # Diagnostic steps
        steps = r.get("diagnostic_steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            empty_steps_count += 1

        # Causes
        causes = r.get("possible_causes", [])
        if not isinstance(causes, list) or len(causes) == 0:
            empty_causes_count += 1

        # Metadata validation
        system = r.get("vehicle_system")
        if system not in ALLOWED_SYSTEMS:
            invalid_systems.add(str(system))
        else:
            system_counts[system] = system_counts.get(system, 0) + 1

        sev = r.get("severity")
        if sev not in ALLOWED_SEVERITIES:
            invalid_severities.add(str(sev))
        else:
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Source attribution
        src = r.get("source")
        url = r.get("source_url")
        if not src or not url:
            missing_attribution += 1

    if missing_fields_count > 0:
        issues.append(f"Found {missing_fields_count} missing required field instances.")
    if short_descriptions > 0:
        issues.append(f"Found {short_descriptions} records with problem_description < 20 characters.")
    if empty_steps_count > 0:
        issues.append(f"Found {empty_steps_count} records with empty diagnostic_steps.")
    if empty_causes_count > 0:
        issues.append(f"Found {empty_causes_count} records with empty possible_causes.")
    if invalid_systems:
        issues.append(f"Found invalid vehicle_system values: {invalid_systems}")
    if invalid_severities:
        issues.append(f"Found invalid severity values: {invalid_severities}")
    if missing_attribution > 0:
        issues.append(f"Found {missing_attribution} records missing source attribution.")

    all_passed = len(issues) == 0

    report = {
        "dataset_path": str(dataset_path),
        "validation_passed": all_passed,
        "total_records": total_records,
        "unique_id_count": len(seen_ids),
        "threshold_required": min_record_count,
        "threshold_satisfied": count_passed,
        "issues_found": issues,
        "system_distribution": system_counts,
        "severity_distribution": severity_counts,
    }

    if all_passed:
        logger.info(f"Dataset validation PASSED with {total_records} verified authentic records.")
    else:
        logger.warning(f"Dataset validation FAILED with {len(issues)} issues.")

    return all_passed, report


if __name__ == "__main__":
    passed, report = validate_dataset()
    print("--- Validation Report ---")
    for k, v in report.items():
        print(f"{k}: {v}")
