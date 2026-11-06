# Data Directory Structure

This directory holds the raw, processed, and query data for the Vehicle Troubleshooting Assistant.

## Subdirectories

- `raw/`: Unmodified authentic data downloads (e.g. Zenodo records, OBD-II definitions, open automotive repositories).
- `processed/`: Validated, standardized, and deduplicated records conforming to the target troubleshooting schema (`vehicle_troubleshooting_dataset.json` / `.parquet`).
- `queries/`: The documented 10 query dataset (`assignment_queries.json`) covering distinct automotive subsystems, student attributions, and expected diagnostic topics.

## Strict Assignment Principles
- All records must come from authentic, verifiable, legally accessible sources.
- No synthetic records are labeled as authentic.
- No duplication to artificially inflate counts.
- Target: At least 5,000 valid, unique vehicle troubleshooting records.
