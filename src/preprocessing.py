"""Dataset preprocessing and standardization engine for Vehicle Troubleshooting records.

Transforms raw heterogeneous automotive diagnostic records (OBDex, SAE J2012,
ISO 15031-6) into a standardized, validated troubleshooting schema with source
attribution, structured metadata, and diagnostic procedures.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import yaml

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.utils import setup_logger, save_json, save_jsonl

logger = setup_logger("preprocessing")


def normalize_text(text: Optional[str]) -> str:
    """Cleans and normalizes text, stripping excessive whitespace."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_multilingual(field: Any, default_lang: str = "en") -> str:
    """Extracts target language string from a bilingual dict or raw string."""
    if isinstance(field, dict):
        return normalize_text(field.get(default_lang) or field.get("en") or "")
    elif isinstance(field, str):
        return normalize_text(field)
    return ""


def determine_severity(record: Dict[str, Any]) -> str:
    """Calculates standardized severity: 'high', 'medium', or 'low'."""
    category = (record.get("category") or "").lower()
    flags = record.get("flags") or {}
    code = (record.get("code") or "").upper()
    repair = record.get("repair") or {}

    # High severity triggers: Safety systems (airbags/SRS), brakes, steering, or limp mode
    if category == "chassis" or "airbag" in str(record).lower() or "srs" in str(record).lower():
        return "high"
    if flags.get("limp_mode_possible", False):
        return "high"
    if repair.get("difficulty") == "hard":
        return "high"

    # Medium severity: Check engine light (MIL), emissions, or powertrain issues
    if flags.get("mil", False) or flags.get("emissions_relevant", False) or category == "powertrain":
        return "medium"

    # Low severity: General electrical/body, accessory
    return "low"


def map_vehicle_system(category: str) -> str:
    """Maps raw diagnostic category to standardized vehicle system."""
    cat = (category or "").lower().strip()
    mapping = {
        "powertrain": "engine_and_transmission",
        "chassis": "brakes_and_suspension",
        "body": "electrical_and_body",
        "network": "network_and_communication",
    }
    return mapping.get(cat, "general_automotive")


def format_symptoms(raw_symptoms: Any) -> List[str]:
    """Formats raw symptoms into a clean list of descriptive strings."""
    symptoms = []
    if isinstance(raw_symptoms, list):
        for s in raw_symptoms:
            text = extract_multilingual(s)
            if text and text not in symptoms:
                symptoms.append(text)
    elif isinstance(raw_symptoms, str) and raw_symptoms.strip():
        symptoms.append(normalize_text(raw_symptoms))
    return symptoms


def format_causes(raw_causes: Any) -> List[str]:
    """Formats common causes with likelihood annotations."""
    causes = []
    if isinstance(raw_causes, list):
        for c in raw_causes:
            if isinstance(c, dict):
                label = extract_multilingual(c.get("label"))
                likelihood = c.get("likelihood")
                if label:
                    formatted = f"{label} (likelihood: {likelihood})" if likelihood else label
                    if formatted not in causes:
                        causes.append(formatted)
            elif isinstance(c, str) and c.strip():
                causes.append(normalize_text(c))
    return causes


def generate_diagnostic_steps(record: Dict[str, Any]) -> List[str]:
    """Generates sequential, actionable diagnostic steps based on fault data."""
    steps = []
    code = record.get("code", "DTC")
    title = extract_multilingual(record.get("title"))
    components = record.get("affected_components") or []
    repair = record.get("repair") or {}

    steps.append(f"Connect OBD-II diagnostic scanner and verify active code {code} ({title}).")
    if components:
        comp_str = ", ".join(str(c).replace("_", " ") for c in components)
        steps.append(f"Perform visual and physical inspection of affected components: {comp_str}.")
    steps.append("Check electrical wiring harnesses and connectors for looseness, corrosion, or pin displacement.")
    steps.append("Measure reference voltage, ground continuity, and component resistance against manufacturer specifications.")

    difficulty = repair.get("difficulty")
    diy = repair.get("diy_possible")
    hours = repair.get("estimated_hours")
    if difficulty or hours:
        diy_str = "DIY feasible" if diy else "Professional technician service recommended"
        labor_str = f"Estimated labor time: {hours[0]}-{hours[1]} hours" if isinstance(hours, list) and len(hours) == 2 else ""
        steps.append(f"Repair guidance: {diy_str}. {labor_str}".strip())

    return steps


def generate_recommended_actions(record: Dict[str, Any]) -> List[str]:
    """Generates concise recommended remediation actions."""
    actions = []
    causes = format_causes(record.get("common_causes"))
    repair = record.get("repair") or {}

    if causes:
        actions.append(f"Prioritize inspection of primary cause: {causes[0]}.")
    if len(causes) > 1:
        actions.append(f"If issue persists, inspect secondary potential fault: {causes[1]}.")

    diy = repair.get("diy_possible")
    if diy is False:
        actions.append("Due to system criticality, have vehicle inspected by an ASE-certified technician.")
    else:
        actions.append("Clear diagnostic trouble codes with scanner after component repair and perform a verification test drive.")

    return actions


def transform_obdex_record(raw: Dict[str, Any], file_source: str) -> Optional[Dict[str, Any]]:
    """Transforms a single raw OBDex record into the standardized schema."""
    code = (raw.get("code") or "").strip().upper()
    if not code:
        return None

    title = extract_multilingual(raw.get("title"))
    description = extract_multilingual(raw.get("description"))

    if not title or not description:
        return None

    # Filter out empty or uninformative placeholder codes (e.g. SAE padding / undefined)
    title_lower = title.lower()
    if "not documented" in title_lower or "no defined meaning" in title_lower or "reserved" in title_lower:
        return None

    category = raw.get("category", "powertrain")
    vehicle_system = map_vehicle_system(category)
    symptoms = format_symptoms(raw.get("symptoms"))
    causes = format_causes(raw.get("common_causes"))

    # A valid troubleshooting record must contain at least one plausible cause
    if not causes:
        return None

    diagnostic_steps = generate_diagnostic_steps(raw)
    recommended_actions = generate_recommended_actions(raw)
    severity = determine_severity(raw)

    unique_id = f"VTR-{code}"

    standardized = {
        "id": unique_id,
        "title": f"DTC {code} - {title}",
        "problem_description": description,
        "symptoms": symptoms,
        "diagnostic_codes": [code],
        "vehicle_system": vehicle_system,
        "possible_causes": causes,
        "diagnostic_steps": diagnostic_steps,
        "recommended_actions": recommended_actions,
        "severity": severity,
        "vehicle_type": "passenger_car_and_light_truck",
        "source": "OBDex / SAE J2012 & ISO 15031-6 Open Diagnostic Standard",
        "source_url": "https://github.com/foerbsnavi/OBDex",
        "source_record_id": code,
        "data_origin": "authentic_open_standard",
        "preprocessing_notes": f"Ingested from {file_source}; standardized into vehicle troubleshooting schema.",
    }
    return standardized


def run_preprocessing(
    raw_dir: Path = RAW_DATA_DIR / "obdex",
    output_json: Path = PROCESSED_DATA_DIR / "vehicle_troubleshooting.json",
    output_jsonl: Path = PROCESSED_DATA_DIR / "vehicle_troubleshooting.jsonl",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Loads raw records, applies transformations, detects duplicates, and exports."""
    logger.info("Starting dataset preprocessing pipeline...")
    raw_files = sorted(raw_dir.glob("*.yaml"))
    if not raw_files:
        raise FileNotFoundError(f"No raw YAML files found in {raw_dir}")

    total_raw_count = 0
    records: List[Dict[str, Any]] = []
    seen_ids = set()
    duplicate_count = 0
    invalid_count = 0
    per_file_counts = {}

    for file_path in raw_files:
        logger.info(f"Processing raw file: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
            if not isinstance(raw_data, list):
                continue
            file_raw_len = len(raw_data)
            total_raw_count += file_raw_len
            file_valid = 0

            for raw_rec in raw_data:
                transformed = transform_obdex_record(raw_rec, file_source=file_path.name)
                if transformed is None:
                    invalid_count += 1
                    continue

                rec_id = transformed["id"]
                if rec_id in seen_ids:
                    duplicate_count += 1
                    continue

                seen_ids.add(rec_id)
                records.append(transformed)
                file_valid += 1

            per_file_counts[file_path.name] = {
                "raw_records": file_raw_len,
                "valid_records": file_valid,
            }

    # Save output files
    logger.info(f"Saving {len(records)} standardized records to {output_json}")
    save_json(records, output_json)
    logger.info(f"Saving {len(records)} standardized records to {output_jsonl}")
    save_jsonl(records, output_jsonl)

    # Compute statistics
    system_distribution: Dict[str, int] = {}
    severity_distribution: Dict[str, int] = {}
    for r in records:
        sys = r["vehicle_system"]
        sev = r["severity"]
        system_distribution[sys] = system_distribution.get(sys, 0) + 1
        severity_distribution[sev] = severity_distribution.get(sev, 0) + 1

    stats = {
        "total_raw_records": total_raw_count,
        "valid_unique_records": len(records),
        "duplicate_records": duplicate_count,
        "invalid_records": invalid_count,
        "system_distribution": system_distribution,
        "severity_distribution": severity_distribution,
        "per_file_counts": per_file_counts,
    }

    logger.info(f"Preprocessing completed. Valid unique records: {len(records)}")
    return records, stats


if __name__ == "__main__":
    records, stats = run_preprocessing()
    print("--- Preprocessing Summary ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
