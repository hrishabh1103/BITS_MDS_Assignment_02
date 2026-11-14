# Automotive Diagnostic Knowledge Base: Data Catalog

**Course:** BITS Pilani WILP — Modern Database Systems (Assignment 2)  
**Project:** Vehicle Troubleshooting Assistant using Persistent ChromaDB and RAG  
**Group:** Group 20  

---

## 1. Dataset Nature & Scope

The dataset comprises **9,532 authentic, unique On-Board Diagnostics (OBD-II) diagnostic trouble code (DTC) knowledge records** conforming to international automotive engineering standards (**SAE J2012** and **ISO 15031-6**).

> **Clarification of Data Type:**  
> This dataset is an engineering knowledge base of standardized Diagnostic Trouble Codes, standard symptom descriptions, and root cause mappings. It is **NOT** a historical repository of 9,532 garage repair orders, shop invoices, or individual customer vehicles.

### Source Derivation vs. Synthesized Guidance
- **Source-Derived Standard Content:**
  - Standardized Diagnostic Trouble Codes (DTCs) across generic powertrain (`P0xxx`, `P2xxx`, `P3xxx`), network communication (`U0xxx`, `U3xxx`), chassis dynamics (`C0xxx`), and body/restraints (`B0xxx`).
  - Standard engineering definitions of fault conditions and electrical Rationality/Circuit/Performance failure modes.
  - Observable vehicle operating symptoms and documented probable causes.
- **Normalized / Structured Guidance:**
  - Standardized step-by-step diagnostic workflows structured into actionable technician inspection steps.
  - Recommended actions and safety warnings normalized to prevent dangerous operations (e.g., SRS pyrotechnic testing, high-voltage battery contact).
  - Categorization into four standardized vehicle subsystems (`engine_and_transmission`, `brakes_and_suspension`, `electrical_and_body`, `network_and_communication`) and three operational severity tiers (`high`, `medium`, `low`).

---

## 2. Actual Repository & Archive Data Files

To keep the submission archive clean, lightweight (under 10 MB), and focused on operational reproducibility, the repository and release package include:

```
data/
├── processed/
│   └── vehicle_troubleshooting.json          # Primary validated dataset (9,532 records, 26 MB uncompressed, ~3 MB compressed)
├── queries/
│   └── assignment_queries.json               # 10 standardized assignment benchmark queries (Q01-Q10)
├── source_inventory.csv                      # Documented investigation of investigated candidate sources
└── README.md                                 # This data documentation file
```

### Archive Inclusions & Exclusions:
- **Included:** `data/processed/vehicle_troubleshooting.json` contains the complete, canonical 9,532 records adhering to the full 16-field schema.
- **Excluded:** Unprocessed raw YAML dumps (`data/raw/obdex/*.yaml`, ~31 MB uncompressed) and redundant line-delimited files (`vehicle_troubleshooting.jsonl`) are excluded from the final submission archive to ensure an efficient package size. If required, raw data can be re-fetched or reprocessed via `python scripts/prepare_dataset.py`.

---

## 3. Dataset Summary & Distributions

- **Total Validated Records:** 9,532 unique DTC records
- **Duplicate Records:** 0 (zero ID collisions)
- **Missing Required Fields:** 0 instances across all 9,532 records
- **License:** Creative Commons Zero 1.0 Universal (**CC0-1.0 Public Domain**)

### Subsystem Distribution
| Subsystem Domain | Internal Key | Validated Records | Percentage |
|---|---|---|---|
| **Engine & Powertrain** | `engine_and_transmission` | 7,354 | 77.15% |
| **Network & Communication** | `network_and_communication` | 1,229 | 12.89% |
| **Chassis, Brakes & Suspension** | `brakes_and_suspension` | 626 | 6.57% |
| **Electrical & Body Systems** | `electrical_and_body` | 323 | 3.39% |
| **Total** | | **9,532** | **100.0%** |

### Severity Distribution
| Severity Level | Definition / Criteria | Record Count | Percentage |
|---|---|---|---|
| **High** | Braking, steering, airbags/SRS, limp-mode activation, severe mechanical risk | 5,694 | 59.74% |
| **Medium** | Check Engine Light (MIL), emissions degradation, sensor circuit faults | 3,326 | 34.89% |
| **Low** | Non-critical body accessories, convenience modules, informational status | 512 | 5.37% |
| **Total** | | **9,532** | **100.0%** |

---

## 4. Record Schema Specification

Each record in `data/processed/vehicle_troubleshooting.json` adheres to the following 16-field JSON schema:

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
    "Connect OBD-II diagnostic scanner and verify active code P0100.",
    "Perform visual and physical inspection of affected components: MAF sensor, intake ducting.",
    "Check electrical wiring harnesses and connectors for looseness, corrosion, or pin displacement.",
    "Measure reference voltage, ground continuity, and component resistance against manufacturer specifications."
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
