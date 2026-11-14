# Benchmark Diagnostic Queries

This directory contains the ten domain-specific automotive benchmark queries formulated for Assignment 2.

## Query Overview (Q01 – Q10)

These queries evaluate dense semantic retrieval, compound metadata filtering, pure NumPy similarity comparisons, and retrieval-augmented generation across multiple vehicle subsystems.

| Query ID | Subsystem | Domain / Complaint | Query Description |
|:---|:---|:---|:---|
| **Q01** | `engine_and_transmission` | Cooling / Overheating | Engine overheating rapidly at highway speeds with boiling coolant in reservoir |
| **Q02** | `engine_and_transmission` | Ignition / Cranking | Engine cranks strongly but fails to start with smell of unburnt fuel and no spark |
| **Q03** | `electrical_and_body` | 12V Battery / Parasitic Drain | Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle |
| **Q04** | `brakes_and_suspension` | Hydraulic Brakes / ABS | Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated |
| **Q05** | `engine_and_transmission` | Transmission / Shudder | Automatic transmission delayed engagement into drive and harsh shudder between 2nd and 3rd gears |
| **Q06** | `engine_and_transmission` | Misfire / Power Loss | Check engine light flashing with rough idling, severe loss of engine power under load |
| **Q07** | `engine_and_transmission` | Fuel Metering / Smoke | Drastic drop in fuel economy with black smoke from exhaust and strong unburnt fuel smell |
| **Q08** | `network_and_communication` | CAN Bus / Communication | Instrument cluster displays multiple failure lamps with total loss of CAN communication between TCM and ECM |
| **Q09** | `electrical_and_body` | SRS Airbag / Clock Spring | Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring |
| **Q10** | `engine_and_transmission` | Turbocharger / Underboost | Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills |

## Schema of `assignment_queries.json`

Each query entry contains:
- `query_id`: Identifier (e.g. `Q01`)
- `topic`: Brief category descriptor
- `subsystem`: Target vehicle subsystem
- `query_text`: Natural-language driver complaint or technician symptom
- `expected_dtc_prefix`: Primary expected DTC category (e.g. `P00B7`, `P0300`, `C0291`)
- `relevance_criteria`: Guidance on what constitutes a diagnostically relevant retrieved record

