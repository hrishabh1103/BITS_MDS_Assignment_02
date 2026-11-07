"""Metadata filter construction and validation engine for ChromaDB queries.

Constructs schema-validated single and compound metadata filters ($and / $or)
for the Vehicle Troubleshooting Knowledge Base.
"""

from typing import Any, Dict, List, Optional
from src.dataset_validator import ALLOWED_SEVERITIES, ALLOWED_SYSTEMS

# Allowed filterable fields in ChromaDB metadata
VALID_METADATA_FIELDS = {
    "vehicle_system": ALLOWED_SYSTEMS,
    "severity": ALLOWED_SEVERITIES,
    "vehicle_type": {"passenger_car_and_light_truck"},
    "data_origin": {"authentic_open_standard"},
    "source": None,  # string match
    "source_record_id": None,
    "id": None,
}


class MetadataFilterBuilder:
    """Builds and validates ChromaDB-compliant metadata filters."""

    @staticmethod
    def equals(field: str, value: Any) -> Dict[str, Any]:
        """Constructs an exact equality condition."""
        MetadataFilterBuilder._validate_field_value(field, value)
        return {field: {"$eq": value}}

    @staticmethod
    def in_list(field: str, values: List[Any]) -> Dict[str, Any]:
        """Constructs an $in condition."""
        if not values or not isinstance(values, list):
            raise ValueError(f"Values for $in on '{field}' must be a non-empty list.")
        for v in values:
            MetadataFilterBuilder._validate_field_value(field, v)
        return {field: {"$in": values}}

    @staticmethod
    def combine_and(conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combines multiple conditions using ChromaDB's $and operator."""
        if not conditions or len(conditions) < 2:
            raise ValueError("ChromaDB $and operator requires at least 2 conditions.")
        return {"$and": conditions}

    @staticmethod
    def combine_or(conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combines multiple conditions using ChromaDB's $or operator."""
        if not conditions or len(conditions) < 2:
            raise ValueError("ChromaDB $or operator requires at least 2 conditions.")
        return {"$or": conditions}

    @staticmethod
    def build_compound_filter(
        vehicle_system: Optional[str] = None,
        severity: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Convenience helper to build validated multi-attribute filter."""
        conditions = []
        if vehicle_system:
            conditions.append(MetadataFilterBuilder.equals("vehicle_system", vehicle_system))
        if severity:
            conditions.append(MetadataFilterBuilder.equals("severity", severity))
        if vehicle_type:
            conditions.append(MetadataFilterBuilder.equals("vehicle_type", vehicle_type))
        if source:
            conditions.append(MetadataFilterBuilder.equals("source", source))

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return MetadataFilterBuilder.combine_and(conditions)

    @staticmethod
    def _validate_field_value(field: str, value: Any) -> None:
        """Validates that field exists and value belongs to allowed enumeration."""
        if field not in VALID_METADATA_FIELDS:
            raise ValueError(
                f"Invalid metadata field '{field}'. Allowed fields: {sorted(VALID_METADATA_FIELDS.keys())}"
            )
        allowed_values = VALID_METADATA_FIELDS[field]
        if allowed_values is not None and value not in allowed_values:
            raise ValueError(
                f"Invalid value '{value}' for metadata field '{field}'. Allowed values: {sorted(allowed_values)}"
            )


# 5 Standard Assignment Metadata Filter Presets (Multi-Condition)
ASSIGNMENT_FILTER_PRESETS = [
    {
        "filter_id": "F01",
        "name": "Brakes & Suspension with High Severity",
        "description": "Restricts search to safety-critical braking, ABS, and stability dynamic failures.",
        "query_text": "Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard",
        "filter": {
            "$and": [
                {"vehicle_system": {"$eq": "brakes_and_suspension"}},
                {"severity": {"$eq": "high"}},
            ]
        },
    },
    {
        "filter_id": "F02",
        "name": "Engine & Transmission with High Severity",
        "description": "Restricts search to catastrophic engine, limp-mode, or severe powertrain faults.",
        "query_text": "Engine overheating rapidly at highway speeds with boiling coolant in reservoir and radiator fan not engaging",
        "filter": {
            "$and": [
                {"vehicle_system": {"$eq": "engine_and_transmission"}},
                {"severity": {"$eq": "high"}},
            ]
        },
    },
    {
        "filter_id": "F03",
        "name": "Network & Communication with High Severity",
        "description": "Restricts search to total loss of CAN bus communications and critical controller timeouts.",
        "query_text": "Instrument cluster displays multiple failure lamps with total loss of CAN communication between engine and transmission control modules",
        "filter": {
            "$and": [
                {"vehicle_system": {"$eq": "network_and_communication"}},
                {"severity": {"$eq": "high"}},
            ]
        },
    },
    {
        "filter_id": "F04",
        "name": "Electrical & Body with High Severity",
        "description": "Restricts search to restraint system (SRS airbag) and safety-critical body electronics.",
        "query_text": "Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring",
        "filter": {
            "$and": [
                {"vehicle_system": {"$eq": "electrical_and_body"}},
                {"severity": {"$eq": "high"}},
            ]
        },
    },
    {
        "filter_id": "F05",
        "name": "Engine & Transmission with Medium Severity",
        "description": "Restricts search to drivability, sensor calibration, and emissions faults with MIL illumination.",
        "query_text": "Drastic drop in fuel economy with black smoke from exhaust and rich fuel mixture odor during acceleration",
        "filter": {
            "$and": [
                {"vehicle_system": {"$eq": "engine_and_transmission"}},
                {"severity": {"$eq": "medium"}},
            ]
        },
    },
]
