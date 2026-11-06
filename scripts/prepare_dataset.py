#!/usr/bin/env python3
"""Script to prepare, standardize, and validate the vehicle troubleshooting dataset.

Usage:
    python scripts/prepare_dataset.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing import run_preprocessing
from src.dataset_validator import validate_dataset
from src.utils import setup_logger

logger = setup_logger("prepare_dataset_script")


def main():
    logger.info("Executing dataset preparation and validation workflow...")
    records, stats = run_preprocessing()

    print("\n" + "=" * 60)
    print("DATASET PREPROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total Raw Records Ingested:    {stats['total_raw_records']}")
    print(f"Valid Unique Records:          {stats['valid_unique_records']}")
    print(f"Duplicate Records Skipped:     {stats['duplicate_records']}")
    print(f"Invalid Records Discarded:     {stats['invalid_records']}")
    print("\nVehicle System Distribution:")
    for sys_name, count in sorted(stats["system_distribution"].items()):
        print(f"  - {sys_name:<28}: {count:>5} records")
    print("\nSeverity Distribution:")
    for sev_name, count in sorted(stats["severity_distribution"].items()):
        print(f"  - {sev_name:<28}: {count:>5} records")

    print("\n" + "=" * 60)
    print("DATASET VALIDATION RUN")
    print("=" * 60)
    passed, report = validate_dataset()
    print(f"Validation Status: {'PASSED' if passed else 'FAILED'}")
    print(f"Total Validated Records: {report.get('total_records', 0)}")
    print(f"5,000 Record Threshold Met: {report.get('threshold_satisfied', False)}")

    if not passed:
        print("\nValidation Issues:")
        for issue in report.get("issues_found", []):
            print(f"  [X] {issue}")
        sys.exit(1)

    print("\nDataset preparation and validation completed successfully.")


if __name__ == "__main__":
    main()
