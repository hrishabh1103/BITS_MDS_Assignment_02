# Vehicle Troubleshooting Knowledge Base: Data Catalog

This directory contains the authentic automotive diagnostic datasets used by the **Vehicle Troubleshooting Assistant using ChromaDB and RAG** for BITS Pilani WILP Modern Database Systems (Assignment 2).

---

## 1. Directory Structure

```
data/
├── raw/
│   └── obdex/                               # Raw unmodified YAML dumps (CC0-1.0 Public Domain)
│       ├── B0xxx_enriched.yaml               # 323 body/SRS airbag codes
│       ├── C0xxx_enriched.yaml               # 626 chassis/ABS/traction control codes
│       ├── P0xxx_enriched.yaml               # 3,705 generic powertrain codes
│       ├── P2xxx_enriched.yaml               # 3,495 extended powertrain/sensor codes
│       ├── P3xxx_enriched.yaml               # 155 auxiliary emissions codes
│       ├── U0xxx_enriched.yaml               # 1,055 network/CAN bus communication codes
│       └── U3xxx_enriched.yaml               # 174 ECU module internal diagnostic codes
│
├── processed/
│   ├── vehicle_troubleshooting.json          # 9,532 standardized JSON records (25 MB)
│   └── vehicle_troubleshooting.jsonl         # 9,532 JSON-Lines records (23 MB)
│
├── queries/
│   └── assignment_queries.json               # 10 assignment query definitions (Phase 4)
│
├── source_inventory.csv                      # Documented inventory of all investigated candidate sources
└── README.md                                 # This document
```

---

## 2. Dataset Verification Summary

- **Total Ingested Raw Records:** 9,533
- **Validated Unique Records:** 9,532
- **Discarded Undocumented Padding Records:** 1 (`VTR-P0FFF` - undocumented placeholder code)
- **Duplicate Records:** 0 (zero duplicate IDs)
- **Target Threshold Satisfied:** **9,532 / 5,000 records (190.6% of requirement)**
- **Authenticity Origin:** 100% authentic, standard-compliant automotive diagnostic records conforming to SAE J2012 and ISO 15031-6 specifications. No synthetic records or artificial duplicates.

---

## 3. Subsystem Breakdown

| Subsystem Category | Internal Key | Validated Records | Share |
|---|---|---|---|
| **Engine & Powertrain** | `engine_and_transmission` | 7,354 | 77.1% |
| **Network & Bus Communication** | `network_and_communication` | 1,229 | 12.9% |
| **Chassis, Brakes & Suspension** | `brakes_and_suspension` | 626 | 6.6% |
| **Electrical & Body Control** | `electrical_and_body` | 323 | 3.4% |
| **Total** | | **9,532** | **100.0%** |

---

## 4. Severity Breakdown

| Severity Level | Criteria | Record Count | Share |
|---|---|---|---|
| **High** | Braking, steering, airbags/SRS, limp mode activation, severe mechanical damage | 5,694 | 59.7% |
| **Medium** | Check engine light (MIL), emissions, sensors, general powertrain | 3,326 | 34.9% |
| **Low** | Non-critical accessory, convenience, informational body modules | 512 | 5.4% |

---

## 5. Schema Definition

Each record adheres to the 16-field standardized JSON schema:

```json
{
  "id": "VTR-P0100",
  "title": "DTC P0100 - Mass or Volume Air Flow Circuit Malfunction",
  "problem_description": "The powertrain control module (PCM) monitors the mass air flow (MAF) sensor circuit...",
  "symptoms": [
    "Check engine light illuminated",
    "Engine hard start or stalling",
    "Hesitation during acceleration"
  ],
  "diagnostic_codes": ["P0100"],
  "vehicle_system": "engine_and_transmission",
  "possible_causes": [
    "MAF sensor connector loose or corroded (likelihood: high)",
    "Contaminated MAF sensor hot-wire element (likelihood: high)",
    "Intake air leak after sensor (likelihood: medium)"
  ],
  "diagnostic_steps": [
    "Connect OBD-II diagnostic scanner and verify active code P0100 (Mass or Volume Air Flow Circuit Malfunction).",
    "Perform visual and physical inspection of affected components: maf sensor, intake ducting.",
    "Check electrical wiring harnesses and connectors for looseness, corrosion, or pin displacement.",
    "Measure reference voltage, ground continuity, and component resistance against manufacturer specifications.",
    "Repair guidance: DIY feasible. Estimated labor time: 0.5-2.0 hours"
  ],
  "recommended_actions": [
    "Prioritize inspection of primary cause: MAF sensor connector loose or corroded.",
    "Clear diagnostic trouble codes with scanner after component repair and perform a verification test drive."
  ],
  "severity": "medium",
  "vehicle_type": "passenger_car_and_light_truck",
  "source": "OBDex / SAE J2012 & ISO 15031-6 Open Diagnostic Standard",
  "source_url": "https://github.com/foerbsnavi/OBDex",
  "source_record_id": "P0100",
  "data_origin": "authentic_open_standard",
  "preprocessing_notes": "Ingested from P0xxx_enriched.yaml; standardized into vehicle troubleshooting schema."
}
```
