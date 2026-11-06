"""Dataset loader module for accessing the processed vehicle troubleshooting records."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import PROCESSED_DATASET_FILE
from src.utils import load_json, setup_logger

logger = setup_logger("dataset_loader")

_CACHED_DATASET: Optional[List[Dict[str, Any]]] = None


def load_processed_dataset(file_path: Optional[Path] = None, force_reload: bool = False) -> List[Dict[str, Any]]:
    """Loads and returns the validated vehicle troubleshooting dataset.

    Uses caching for performance across subsequent module invocations.
    """
    global _CACHED_DATASET
    if _CACHED_DATASET is not None and not force_reload:
        return _CACHED_DATASET

    target_path = file_path or PROCESSED_DATASET_FILE
    if not target_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {target_path}. Run scripts/prepare_dataset.py first.")

    logger.info(f"Loading processed dataset from {target_path}...")
    data = load_json(target_path)
    if not isinstance(data, list):
        raise ValueError(f"Expected list of records, got {type(data)}")

    _CACHED_DATASET = data
    logger.info(f"Loaded {len(data)} vehicle troubleshooting records successfully.")
    return data


def get_record_by_id(record_id: str, file_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single troubleshooting record by its unique ID."""
    dataset = load_processed_dataset(file_path)
    for record in dataset:
        if record.get("id") == record_id:
            return record
    return None


def get_dataset_summary(file_path: Optional[Path] = None) -> Dict[str, Any]:
    """Computes a high-level statistical summary of the dataset."""
    dataset = load_processed_dataset(file_path)
    system_counts: Dict[str, int] = {}
    severity_counts: Dict[str, int] = {}

    for r in dataset:
        sys = r.get("vehicle_system", "unknown")
        sev = r.get("severity", "unknown")
        system_counts[sys] = system_counts.get(sys, 0) + 1
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "total_records": len(dataset),
        "system_distribution": system_counts,
        "severity_distribution": severity_counts,
    }
