# Multi-Condition Metadata Filtering Experiment Results

**Collection:** `vehicle_troubleshooting_kb`  
**Experiments Executed:** 5 multi-condition filters  
**Execution Timestamp:** 2026-11-07T07:47:09Z  

---

## Filter Design & Verification Overview

ChromaDB enforces metadata filtering using structured boolean operator objects (`$and`, `$or`). Each experiment below verifies that compound filter constraints are strictly obeyed, preventing domain cross-talk and restricting search space to authenticated subsystem partitions.

---

### Experiment F01: Brakes & Suspension with High Severity
**Description:** Restricts search to safety-critical braking, ABS, and stability dynamic failures.  
**Query Text:** *"Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard"*  
**Filter Expression:** `{'$and': [{'vehicle_system': {'$eq': 'brakes_and_suspension'}}, {'severity': {'$eq': 'high'}}]}`  
**Results Found:** 5 records  

| Rank | Record ID | Title | Distance | Severity | Vehicle System |
|---|---|---|---|---|---|
| 1 | `VTR-C0291` | DTC C0291 - Brake Pedal Apply Sensor Circuit  | 0.4759 | `high` | `brakes_and_suspension` |
| 2 | `VTR-C0081` | DTC C0081 - ABS Malfunction Indicator | 0.4847 | `high` | `brakes_and_suspension` |
| 3 | `VTR-C0082` | DTC C0082 - Brake System Malfunction Indicato | 0.4898 | `high` | `brakes_and_suspension` |
| 4 | `VTR-C0241` | DTC C0241 - ABS Warning Lamp Control Circuit | 0.4903 | `high` | `brakes_and_suspension` |
| 5 | `VTR-C0075` | DTC C0075 - Brake Pedal Position Performance | 0.4981 | `high` | `brakes_and_suspension` |

**Compliance Check:** All returned records verified matching filter criteria.

---

### Experiment F02: Engine & Transmission with High Severity
**Description:** Restricts search to catastrophic engine, limp-mode, or severe powertrain faults.  
**Query Text:** *"Engine overheating rapidly at highway speeds with boiling coolant in reservoir and radiator fan not engaging"*  
**Filter Expression:** `{'$and': [{'vehicle_system': {'$eq': 'engine_and_transmission'}}, {'severity': {'$eq': 'high'}}]}`  
**Results Found:** 5 records  

| Rank | Record ID | Title | Distance | Severity | Vehicle System |
|---|---|---|---|---|---|
| 1 | `VTR-P2B61` | DTC P2B61 - Engine Coolant Flow Control Valve | 0.6509 | `high` | `engine_and_transmission` |
| 2 | `VTR-P26CB` | DTC P26CB - Engine Coolant Pump Performance/S | 0.6723 | `high` | `engine_and_transmission` |
| 3 | `VTR-P0117` | DTC P0117 - Engine Coolant Temperature Sensor | 0.6754 | `high` | `engine_and_transmission` |
| 4 | `VTR-P2B58` | DTC P2B58 - Engine Coolant Flow Control Valve | 0.6880 | `high` | `engine_and_transmission` |
| 5 | `VTR-P26D2` | DTC P26D2 - Engine Coolant Pump Control Modul | 0.6936 | `high` | `engine_and_transmission` |

**Compliance Check:** All returned records verified matching filter criteria.

---

### Experiment F03: Network & Communication with High Severity
**Description:** Restricts search to total loss of CAN bus communications and critical controller timeouts.  
**Query Text:** *"Instrument cluster displays multiple failure lamps with total loss of CAN communication between engine and transmission control modules"*  
**Filter Expression:** `{'$and': [{'vehicle_system': {'$eq': 'network_and_communication'}}, {'severity': {'$eq': 'high'}}]}`  
**Results Found:** 5 records  

| Rank | Record ID | Title | Distance | Severity | Vehicle System |
|---|---|---|---|---|---|
| 1 | `VTR-U0039` | DTC U0039 - Vehicle Communication Bus B (+) O | 0.5003 | `high` | `network_and_communication` |
| 2 | `VTR-U007E` | DTC U007E - Control Module Communication Bus  | 0.5102 | `high` | `network_and_communication` |
| 3 | `VTR-U0094` | DTC U0094 - Vehicle Communication Bus H (+) O | 0.5139 | `high` | `network_and_communication` |
| 4 | `VTR-U0066` | DTC U0066 - Vehicle Communication Bus E (+) O | 0.5270 | `high` | `network_and_communication` |
| 5 | `VTR-U007A` | DTC U007A - Control Module Communication Bus  | 0.5424 | `high` | `network_and_communication` |

**Compliance Check:** All returned records verified matching filter criteria.

---

### Experiment F04: Electrical & Body with High Severity
**Description:** Restricts search to restraint system (SRS airbag) and safety-critical body electronics.  
**Query Text:** *"Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring"*  
**Filter Expression:** `{'$and': [{'vehicle_system': {'$eq': 'electrical_and_body'}}, {'severity': {'$eq': 'high'}}]}`  
**Results Found:** 5 records  

| Rank | Record ID | Title | Distance | Severity | Vehicle System |
|---|---|---|---|---|---|
| 1 | `VTR-B0005` | DTC B0005 - Collapsible Steering Column Deplo | 0.4656 | `high` | `electrical_and_body` |
| 2 | `VTR-B0061` | DTC B0061 - Passenger Seat Belt Tension Senso | 0.5270 | `high` | `electrical_and_body` |
| 3 | `VTR-B0001` | DTC B0001 - Driver Frontal Stage 1 Deployment | 0.5272 | `high` | `electrical_and_body` |
| 4 | `VTR-B0051` | DTC B0051 - First Row Center Seat Belt Sensor | 0.5391 | `high` | `electrical_and_body` |
| 5 | `VTR-B00D5` | DTC B00D5 - Restraint System Passenger Disabl | 0.5441 | `high` | `electrical_and_body` |

**Compliance Check:** All returned records verified matching filter criteria.

---

### Experiment F05: Engine & Transmission with Medium Severity
**Description:** Restricts search to drivability, sensor calibration, and emissions faults with MIL illumination.  
**Query Text:** *"Drastic drop in fuel economy with black smoke from exhaust and rich fuel mixture odor during acceleration"*  
**Filter Expression:** `{'$and': [{'vehicle_system': {'$eq': 'engine_and_transmission'}}, {'severity': {'$eq': 'medium'}}]}`  
**Results Found:** 5 records  

| Rank | Record ID | Title | Distance | Severity | Vehicle System |
|---|---|---|---|---|---|
| 1 | `VTR-P2BD2` | DTC P2BD2 - Exhaust Aftertreatment System A L | 0.6449 | `medium` | `engine_and_transmission` |
| 2 | `VTR-P0313` | DTC P0313 - Misfire Detected with Low Fuel | 0.6739 | `medium` | `engine_and_transmission` |
| 3 | `VTR-P0446` | DTC P0446 - EVAP System Vent Control Circuit | 0.6817 | `medium` | `engine_and_transmission` |
| 4 | `VTR-P2C79` | DTC P2C79 - NOx Adsorber - Sulfur Limit Excee | 0.6848 | `medium` | `engine_and_transmission` |
| 5 | `VTR-P04DF` | DTC P04DF - EVAP System Purge Control Valve A | 0.6911 | `medium` | `engine_and_transmission` |

**Compliance Check:** All returned records verified matching filter criteria.

---
