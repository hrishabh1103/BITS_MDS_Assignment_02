# Semantic Search & Top-K Retrieval Experiment Results

**Collection:** `vehicle_troubleshooting_kb`  
**Total Indexed Documents:** 9,532  
**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)  
**Distance Metric:** `cosine` (Cosine distance: 0.0 = identical, 1.0 = orthogonal)  
**Execution Timestamp:** 2026-11-07T07:47:09Z  

---

## Executive Summary

Each of the 10 diverse automotive troubleshooting queries was executed against the persistent ChromaDB database for both **K=5** and **K=10**. All result lists are strictly ranked by cosine distance (ascending). Zero ID collisions were detected in any query result list.

---

### Query Q01: Engine Cooling & Thermal Management
**Query Text:** *"Engine overheating rapidly at highway speeds with boiling coolant in reservoir and radiator fan not engaging"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Tests retrieval for cooling system failures, radiator fan relay/circuit faults, and thermostat malfunctions causing severe engine overheating.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P00B7` | DTC P00B7 - Engine Coolant Flow Low/Performan | 0.6039 | 0.3961 | `medium` | `engine_and_transmission` |
| 2 | `VTR-P2B61` | DTC P2B61 - Engine Coolant Flow Control Valve | 0.6509 | 0.3491 | `high` | `engine_and_transmission` |
| 3 | `VTR-U0698` | DTC U0698 - Lost Communication With Coolant P | 0.6616 | 0.3384 | `high` | `network_and_communication` |
| 4 | `VTR-P2D8A` | DTC P2D8A - Fan 2 Control Module Over Tempera | 0.6687 | 0.3313 | `medium` | `engine_and_transmission` |
| 5 | `VTR-P26CB` | DTC P26CB - Engine Coolant Pump Performance/S | 0.6723 | 0.3277 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P00B7 - Engine Coolant Flow Low/Performance** (`VTR-P00B7`):  
> When the engine is hot, the thermostat should be open and coolant should flow through the radiator. P00B7 is set when the engine coolant temperature is very high (above about 117 to 119 °C in documented cases) while the radiator side stays much colde...

---

### Query Q02: Ignition & Starting System Malfunction
**Query Text:** *"Engine cranks strongly but fails to start with smell of unburnt fuel and no spark on ignition coils"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Addresses primary starting failure where starter motor operates but lack of ignition signal or crankshaft position sensor input prevents combustion.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P0316` | DTC P0316 - Engine Misfire Detected on Startu | 0.6113 | 0.3887 | `medium` | `engine_and_transmission` |
| 2 | `VTR-P2314` | DTC P2314 - Ignition Coil E Secondary Circuit | 0.6183 | 0.3817 | `high` | `engine_and_transmission` |
| 3 | `VTR-P2E5C` | DTC P2E5C - Cylinder 4 Alternative Fuel Misfi | 0.6234 | 0.3766 | `high` | `engine_and_transmission` |
| 4 | `VTR-P2E5E` | DTC P2E5E - Cylinder 6 Alternative Fuel Misfi | 0.6371 | 0.3629 | `high` | `engine_and_transmission` |
| 5 | `VTR-P2A2F` | DTC P2A2F - Alternative Fuel Tank Shutoff Val | 0.6373 | 0.3627 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P0316 - Engine Misfire Detected on Startup (First 1000 Revolutions)** (`VTR-P0316`):  
> P0316 concerns misfire within the first 1,000 revolutions after start. CARB requires a pending code here after the first exceedance of the emissions-relevant rate (later in the drive only after the fourth) and the warning light if it recurs at the ne...

---

### Query Q03: Parasitic Battery Drain & Body Electrical
**Query Text:** *"Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle"*  
**Subsystem:** `electrical_and_body`  
**Diagnostic Rationale:** Diagnoses quiescent parasitic battery discharge caused by body control modules, relays, or lighting circuits staying awake when ignition is off.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P0D17` | DTC P0D17 - Battery Charging System A High Vo | 0.5376 | 0.4624 | `medium` | `engine_and_transmission` |
| 2 | `VTR-P0B57` | DTC P0B57 - Hybrid/EV Battery Voltage Sense F | 0.5690 | 0.4310 | `high` | `engine_and_transmission` |
| 3 | `VTR-P0D46` | DTC P0D46 - Battery Charger 14 Volt Output Vo | 0.5712 | 0.4288 | `medium` | `engine_and_transmission` |
| 4 | `VTR-P0D47` | DTC P0D47 - Battery Charger 14 Volt Output Cu | 0.5735 | 0.4265 | `medium` | `engine_and_transmission` |
| 5 | `VTR-P0D23` | DTC P0D23 - Battery Charger A Output Shorted | 0.5757 | 0.4243 | `medium` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P0D17 - Battery Charging System A High Voltage Interlock Circuit Low** (`VTR-P0D17`):  
> P0D17 means the sensed voltage of the charging HVIL loop is too low. GM documents the check for the Chevrolet Volt (2011, 2014) and the Cadillac ELR: while the module sources 5 V into the loop, a sensed value under 30 % of the reference in two sample...

---

### Query Q04: Braking Hydraulics & Anti-Lock Braking System
**Query Text:** *"Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard"*  
**Subsystem:** `brakes_and_suspension`  
**Diagnostic Rationale:** Evaluates critical hydraulic brake failure symptoms including master cylinder internal bypass, ABS modulator valve leakage, and brake fluid pressure drop.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-C0291` | DTC C0291 - Brake Pedal Apply Sensor Circuit  | 0.4759 | 0.5241 | `high` | `brakes_and_suspension` |
| 2 | `VTR-C0081` | DTC C0081 - ABS Malfunction Indicator | 0.4847 | 0.5153 | `high` | `brakes_and_suspension` |
| 3 | `VTR-C0082` | DTC C0082 - Brake System Malfunction Indicato | 0.4898 | 0.5102 | `high` | `brakes_and_suspension` |
| 4 | `VTR-C0241` | DTC C0241 - ABS Warning Lamp Control Circuit | 0.4903 | 0.5097 | `high` | `brakes_and_suspension` |
| 5 | `VTR-C0075` | DTC C0075 - Brake Pedal Position Performance | 0.4981 | 0.5019 | `high` | `brakes_and_suspension` |

**Top Match Excerpt:**
> **DTC C0291 - Brake Pedal Apply Sensor Circuit Malfunction** (`VTR-C0291`):  
> Electrical fault in the brake pedal apply sensor circuit. The module cannot reliably detect whether the brake pedal is pressed, which affects ABS, ESP and brake assist functions.

---

### Query Q05: Automatic Transmission & Shift Solenoids
**Query Text:** *"Automatic transmission delayed engagement into drive and harsh shuddering when shifting between second and third gears"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Investigates transmission hydraulic pressure loss, shift solenoid electrical malfunctions, and torque converter clutch slippage.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P2711` | DTC P2711 - Unexpected Mechanical Gear Diseng | 0.5015 | 0.4985 | `high` | `engine_and_transmission` |
| 2 | `VTR-P0733` | DTC P0733 - Gear 3 Incorrect Ratio | 0.5524 | 0.4476 | `high` | `engine_and_transmission` |
| 3 | `VTR-P2E14` | DTC P2E14 - Gear Selection Actuator Position  | 0.5553 | 0.4447 | `high` | `engine_and_transmission` |
| 4 | `VTR-P0918` | DTC P0918 - Gear Shift Position Circuit A Int | 0.5624 | 0.4376 | `high` | `engine_and_transmission` |
| 5 | `VTR-P2701` | DTC P2701 - Transmission Friction Element B A | 0.5625 | 0.4375 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P2711 - Unexpected Mechanical Gear Disengagement** (`VTR-P2711`):  
> P2711 is set when the transmission controller sees the drivetrain act as if a gear were no longer properly engaged although it never commanded that, for example because a clutch drags or a gear does not engage as selected. Volkswagen Group uses it on...

---

### Query Q06: Engine Misfire & Cylinder Combustion Faults
**Query Text:** *"Check engine light flashing with rough idling, severe loss of engine power, and heavy vehicle vibration under load"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Focuses on catastrophic catalyst-damaging misfires caused by bad fuel injectors, worn spark plugs, or ignition coil circuit failures.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-B0860` | DTC B0860 - License Plate Lamp Circuit | 0.5494 | 0.4506 | `low` | `electrical_and_body` |
| 2 | `VTR-B00D3` | DTC B00D3 - Restraint System Malfunction Indi | 0.5589 | 0.4411 | `high` | `electrical_and_body` |
| 3 | `VTR-C05F2` | DTC C05F2 - Rear Drive Shaft Speed Sensor Cir | 0.5635 | 0.4365 | `high` | `brakes_and_suspension` |
| 4 | `VTR-B00D4` | DTC B00D4 - Restraint System Malfunction Audi | 0.5733 | 0.4267 | `high` | `electrical_and_body` |
| 5 | `VTR-P2582` | DTC P2582 - Turbocharger/Supercharger Speed S | 0.5771 | 0.4229 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC B0860 - License Plate Lamp Circuit** (`VTR-B0860`):  
> A fault has been detected in the license plate lamp circuit.

---

### Query Q07: Fuel & Air Metering / Rich Mixture
**Query Text:** *"Drastic drop in fuel economy with black smoke from exhaust and rich fuel mixture odor during acceleration"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Retrieves faults related to MAF sensor contamination, leaking fuel pressure regulators, or upstream oxygen sensor bias causing rich fuel trim.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P2BD2` | DTC P2BD2 - Exhaust Aftertreatment System A L | 0.6449 | 0.3551 | `medium` | `engine_and_transmission` |
| 2 | `VTR-P20D5` | DTC P20D5 - Exhaust Aftertreatment Fuel Injec | 0.6503 | 0.3497 | `high` | `engine_and_transmission` |
| 3 | `VTR-P20CF` | DTC P20CF - Exhaust Aftertreatment Fuel Injec | 0.6683 | 0.3317 | `high` | `engine_and_transmission` |
| 4 | `VTR-P02ED` | DTC P02ED - Diesel Intake Air Flow A Control  | 0.6688 | 0.3312 | `high` | `engine_and_transmission` |
| 5 | `VTR-P24A3` | DTC P24A3 - Particulate Filter Restriction -  | 0.6699 | 0.3301 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P2BD2 - Exhaust Aftertreatment System A Leak** (`VTR-P2BD2`):  
> P2BD2 reports that the first aftertreatment line, or the only one, is not gas-tight, so exhaust escapes between engine and tailpipe or false air enters. A leak upstream of the catalysts lets untreated NOx and soot out and also confuses sensors: Foton...

---

### Query Q08: CAN Bus & Inter-Module Network Communication
**Query Text:** *"Instrument cluster displays multiple failure lamps with total loss of CAN communication between engine and transmission control modules"*  
**Subsystem:** `network_and_communication`  
**Diagnostic Rationale:** Investigates vehicle serial data network failures (U0100/U0101 family), bus termination resistor faults, and lost communication between primary powertrain controllers.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-B0223` | DTC B0223 - SRS Indicator Lamp Circuit Malfun | 0.4971 | 0.5029 | `high` | `electrical_and_body` |
| 2 | `VTR-P0804` | DTC P0804 - Upshift/Skip Shift Lamp Control C | 0.5001 | 0.4999 | `medium` | `engine_and_transmission` |
| 3 | `VTR-U0039` | DTC U0039 - Vehicle Communication Bus B (+) O | 0.5003 | 0.4997 | `high` | `network_and_communication` |
| 4 | `VTR-U007E` | DTC U007E - Control Module Communication Bus  | 0.5102 | 0.4898 | `high` | `network_and_communication` |
| 5 | `VTR-U0094` | DTC U0094 - Vehicle Communication Bus H (+) O | 0.5139 | 0.4861 | `high` | `network_and_communication` |

**Top Match Excerpt:**
> **DTC B0223 - SRS Indicator Lamp Circuit Malfunction** (`VTR-B0223`):  
> The SRS module has detected a fault in the airbag warning lamp circuit. The lamp may be inoperative, which prevents driver notification of stored faults.

---

### Query Q09: Supplemental Restraint System (SRS) & Airbag Circuit
**Query Text:** *"Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring"*  
**Subsystem:** `electrical_and_body`  
**Diagnostic Rationale:** Tests safety restraint diagnostic retrieval, driver airbag squib deployment circuits, and steering wheel clock spring resistance faults (B0001/B0002).  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-B0005` | DTC B0005 - Collapsible Steering Column Deplo | 0.4656 | 0.5344 | `high` | `electrical_and_body` |
| 2 | `VTR-B0061` | DTC B0061 - Passenger Seat Belt Tension Senso | 0.5270 | 0.4730 | `high` | `electrical_and_body` |
| 3 | `VTR-B0001` | DTC B0001 - Driver Frontal Stage 1 Deployment | 0.5272 | 0.4728 | `high` | `electrical_and_body` |
| 4 | `VTR-U047B` | DTC U047B - Invalid Data Received From Restra | 0.5338 | 0.4662 | `high` | `network_and_communication` |
| 5 | `VTR-B0051` | DTC B0051 - First Row Center Seat Belt Sensor | 0.5391 | 0.4609 | `high` | `electrical_and_body` |

**Top Match Excerpt:**
> **DTC B0005 - Collapsible Steering Column Deployment Control** (`VTR-B0005`):  
> The SRS module detects an open circuit in the driver frontal airbag deployment loop. The airbag will not deploy in a crash and the SRS warning lamp is illuminated.

---

### Query Q10: Turbocharger Forced Induction & Boost Control
**Query Text:** *"Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills"*  
**Subsystem:** `engine_and_transmission`  
**Diagnostic Rationale:** Evaluates forced induction troubleshooting including turbocharger wastegate control solenoid faults, charge air boost leaks, and manifold absolute pressure sensor discrepancies.  

#### Top-5 Retrieved Records:

| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |
|---|---|---|---|---|---|---|
| 1 | `VTR-P0299` | DTC P0299 - Turbocharger/Supercharger A Under | 0.4707 | 0.5293 | `high` | `engine_and_transmission` |
| 2 | `VTR-P0048` | DTC P0048 - Turbocharger/Supercharger Boost C | 0.4835 | 0.5165 | `high` | `engine_and_transmission` |
| 3 | `VTR-P0046` | DTC P0046 - Turbocharger/Supercharger Boost C | 0.4982 | 0.5018 | `high` | `engine_and_transmission` |
| 4 | `VTR-P0047` | DTC P0047 - Turbocharger/Supercharger Boost C | 0.5017 | 0.4983 | `high` | `engine_and_transmission` |
| 5 | `VTR-P02CA` | DTC P02CA - Turbocharger/Supercharger B Overb | 0.5084 | 0.4916 | `high` | `engine_and_transmission` |

**Top Match Excerpt:**
> **DTC P0299 - Turbocharger/Supercharger A Underboost Condition** (`VTR-P0299`):  
> P0299 means actual boost stays below target for a period although the control already demands more. Thresholds: GM petrol 30–55 kPa below target with the warning light in the first trip; GM diesels 10–50 kPa, two trips; Ford EcoBoost more than 4 psi ...

---
