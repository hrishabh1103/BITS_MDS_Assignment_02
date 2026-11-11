"""Automotive Safety Guardrails and Domain Validation Engine.

Provides deep domain verification and automated safety warnings for:
1. Supplemental Restraint Systems (SRS / Airbags): Prohibits ohmmeter probing across squibs.
2. High-Voltage Hybrid/Electric Vehicle Systems: Enforces 400V/800V shock hazard warnings and PPE protocols.
3. ICE 12V Battery Drain vs. EV Charger Mismatch: Catches and resolves context mismatches where EV records are retrieved for ICE alternator systems.
4. Hydraulic Braking Failures: Detects sinking/soft pedals, mandates immediate towing, forbids road driving.
5. Engine Cooling & Thermal Systems: Scald/burn hazard warnings on pressurized boiling cooling systems.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass
class SafetyAlert:
    """Structured automotive safety alert rendered in backend outputs and UI."""
    category: str       # 'SRS_AIRBAG', 'HIGH_VOLTAGE_EV', 'BRAKING_HAZARD', 'THERMAL_SCALD', 'DOMAIN_MISMATCH'
    severity: str       # 'DANGER', 'CRITICAL', 'WARNING', 'NOTICE'
    title: str
    message: str
    recommended_action: str


# SRS / Airbag specific indicators (not generic B-codes)
SRS_AIRBAG_KEYWORDS = [
    "airbag", "srs", "clock spring", "clockspring", "spiral cable", "supplemental restraint",
    "squib", "seat belt pretensioner", "seatbelt pretensioner", "curtain airbag",
    "knee airbag", "side airbag", "frontal stage", "deployment control", "restraint system"
]
SRS_AIRBAG_DTC_PREFIXES = ["B000", "B001", "B002", "B003", "B004", "B005", "B006", "B007", "B008", "B009", "U047"]

# High-voltage EV / Hybrid indicators
HV_EV_KEYWORDS = [
    "high voltage", "high-voltage", "hvil", "traction battery", "inverter", "converter",
    "hybrid battery", "ev battery", "electric vehicle", "battery charger 14 v", "onboard charger",
    "hv interlock", "high potential", "dc-dc converter"
]
HV_EV_DTC_PREFIXES = ["P0B", "P0C", "P0D", "P1A", "P1B"]

# 12V ICE battery drain indicators
ICE_12V_DRAIN_KEYWORDS = [
    "battery goes dead", "dead overnight", "parasitic draw", "parasitic drain", "battery drain",
    "alternator charging", "alternator", "12v battery", "discharging overnight"
]

# Hydraulic braking failure indicators
BRAKE_HAZARD_KEYWORDS = [
    "pedal sinks", "pedal sinking", "sinking to floor", "sinks slowly", "floorboard",
    "soft pedal", "spongy pedal", "pedal goes to floor", "loss of braking", "brake failure",
    "fluid leak", "master cylinder bypass"
]

# Thermal / cooling system indicators
COOLING_SCALD_KEYWORDS = [
    "overheating", "overheat", "boiling coolant", "steam", "hot coolant", "coolant reservoir",
    "radiator cap", "coolant boiling", "coolant blowing"
]


def detect_safety_triggers(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    vehicle_type: str = "Unknown",
) -> Dict[str, Any]:
    """Analyzes user query, retrieved context, and vehicle type to detect critical safety triggers."""
    q_lower = query.lower()
    docs_text = " ".join([
        (d.get("title", "") + " " + d.get("document", "") + " " + d.get("diagnostic_codes", "")).lower()
        for d in retrieved_docs
    ])

    # 1. SRS / Airbag Detection (Targeted keywords or specific SRS DTCs, NOT any B-code)
    has_srs_query = any(k in q_lower for k in SRS_AIRBAG_KEYWORDS)
    has_srs_dtc = any(
        any(doc.get("diagnostic_codes", "").startswith(prefix) for prefix in SRS_AIRBAG_DTC_PREFIXES)
        for doc in retrieved_docs
    )
    has_srs_doc_text = any(k in docs_text for k in SRS_AIRBAG_KEYWORDS)
    is_srs = has_srs_query or (has_srs_dtc and has_srs_doc_text)

    # 2. High-Voltage EV Detection
    has_hv_query = any(k in q_lower for k in HV_EV_KEYWORDS) or vehicle_type in ("Hybrid", "EV")
    has_hv_dtc = any(
        any(doc.get("diagnostic_codes", "").startswith(prefix) for prefix in HV_EV_DTC_PREFIXES)
        for doc in retrieved_docs
    )
    has_hv_doc_text = any(k in docs_text for k in HV_EV_KEYWORDS)
    is_hv = has_hv_query or has_hv_dtc or has_hv_doc_text

    # 3. ICE 12V Battery Drain vs. EV Charger Context Mismatch
    is_12v_drain_query = any(k in q_lower for k in ICE_12V_DRAIN_KEYWORDS)
    is_ice_vehicle = (vehicle_type == "ICE") or ("alternator" in q_lower and vehicle_type != "EV")
    # If the user asks about an ordinary 12V drain/alternator but context contains high-voltage EV charger codes
    is_mismatch = is_12v_drain_query and is_ice_vehicle and has_hv_dtc

    # 4. Braking Hydraulic Hazard Detection
    is_braking = any(k in q_lower for k in BRAKE_HAZARD_KEYWORDS) or (
        "brake" in q_lower and ("sink" in q_lower or "floor" in q_lower or "soft" in q_lower or "leak" in q_lower)
    )

    # 5. Thermal Scald / Overheating Detection
    is_cooling = any(k in q_lower for k in COOLING_SCALD_KEYWORDS)

    return {
        "srs_airbag": is_srs,
        "high_voltage_ev": is_hv,
        "ice_12v_battery_mismatch": is_mismatch,
        "braking_hydraulic": is_braking,
        "cooling_thermal": is_cooling,
        "vehicle_type": vehicle_type,
    }


def generate_safety_alerts(triggers: Dict[str, Any]) -> List[SafetyAlert]:
    """Generates authoritative, highly visible safety alerts based on detected triggers."""
    alerts = []

    # A. SRS / Airbag Safety Alert
    if triggers.get("srs_airbag"):
        alerts.append(SafetyAlert(
            category="SRS_AIRBAG",
            severity="DANGER",
            title="DANGER: Supplemental Restraint System (SRS / Airbag) Safety Hazard",
            message=(
                "NEVER use an ohmmeter, multimeter, or test light to measure resistance across airbag squibs, "
                "steering wheel clock springs, or deployment loop terminals. The tiny metering current from standard "
                "multimeters can trigger instantaneous pyrotechnic airbag deployment, causing fatal injuries or severe trauma. "
                "Never apply external voltage to restraint wiring. Wire colors and pinouts must only be referenced from "
                "official OEM service manuals."
            ),
            recommended_action=(
                "Immediately disconnect the 12V battery negative terminal and wait at least 3 minutes to discharge the "
                "SRS backup power capacitor before touching any restraint wiring. Refer diagnostics to an ASE-certified technician."
            ),
        ))

    # B. High-Voltage EV Safety Alert
    if triggers.get("high_voltage_ev") and not triggers.get("ice_12v_battery_mismatch"):
        alerts.append(SafetyAlert(
            category="HIGH_VOLTAGE_EV",
            severity="DANGER",
            title="DANGER: High-Voltage Hybrid/Electric Vehicle System (300V - 800V DC)",
            message=(
                "High-voltage hybrid and electric vehicle systems carry lethal DC potentials (300V–800V). "
                "NEVER touch, probe, or cut orange high-voltage cables. NEVER open traction inverters, DC-DC converters, "
                "or high-voltage battery enclosures without Class 0 (1,000V rated) insulated gloves and an official manual disconnect."
            ),
            recommended_action=(
                "High-voltage diagnostics must be performed exclusively by qualified EV technicians following factory high-voltage "
                "isolation and lockout/tagout (LOTO) protocols."
            ),
        ))

    # C. ICE 12V Battery Drain vs EV Charger Mismatch Notice
    if triggers.get("ice_12v_battery_mismatch"):
        alerts.append(SafetyAlert(
            category="DOMAIN_MISMATCH",
            severity="WARNING",
            title="DOMAIN MISMATCH WARNING: 12V ICE Electrical System vs. Retrieved EV Records",
            message=(
                "The symptom describes a conventional 12V automotive battery drain with an internal combustion engine alternator. "
                "However, the dense retrieval engine returned High-Voltage EV/Hybrid charging records (e.g. DTC P0D17, P0D46, P0D23). "
                "These EV high-voltage interlock loop (HVIL) codes DO NOT apply to an ordinary 12V automotive battery drain."
            ),
            recommended_action=(
                "Do NOT inspect high-voltage EV components for an ordinary alternator/battery issue. Perform standard 12V parasitic draw "
                "testing using a digital multimeter in series with the battery negative post, or conduct millivolt-drop measurements across "
                "the interior and underhood fuse blocks to isolate parasitic circuit draw."
            ),
        ))

    # D. Braking Hydraulic Hazard Alert
    if triggers.get("braking_hydraulic"):
        alerts.append(SafetyAlert(
            category="BRAKING_HAZARD",
            severity="CRITICAL",
            title="CRITICAL SAFETY HAZARD: Hydraulic Brake Failure — DO NOT DRIVE",
            message=(
                "A brake pedal sinking slowly to the floorboard at red lights indicates an internal master cylinder piston seal bypass, "
                "air in the hydraulic lines, or an external fluid leak. The vehicle is UNSAFE TO DRIVE and represents an immediate catastrophic "
                "stopping failure risk on public roads. Do not assume the brakes are functional because an ABS code is present."
            ),
            recommended_action=(
                "Do NOT drive the vehicle under any circumstances. Have the vehicle towed to an ASE-certified repair facility "
                "for master cylinder replacement, hydraulic pressure testing, and professional bleeding."
            ),
        ))

    # E. Cooling System Scald Hazard Alert
    if triggers.get("cooling_thermal"):
        alerts.append(SafetyAlert(
            category="THERMAL_SCALD",
            severity="WARNING",
            title="SCALD HAZARD: Pressurized High-Temperature Engine Coolant",
            message=(
                "Engine coolant under operating conditions reaches temperatures above 100°C (212°F) under pressure (15–20 psi). "
                "NEVER attempt to open the radiator cap, degas bottle, or coolant reservoir while the engine is hot. Rapid depressurization "
                "will cause boiling coolant to erupt instantly, causing severe third-degree burns."
            ),
            recommended_action=(
                "Allow the vehicle to cool down for at least 45 to 60 minutes until hoses are cool to the touch before checking "
                "coolant level or inspecting cooling system components."
            ),
        ))

    return alerts


def build_safety_augmented_instructions(triggers: Dict[str, Any]) -> str:
    """Builds specific system prompt instructions dynamically injected based on active triggers."""
    rules = []

    if triggers.get("srs_airbag"):
        rules.append(
            "CRITICAL SRS/AIRBAG DIRECTIVE: This query involves Supplemental Restraint Systems. "
            "You MUST explicitly forbid the user or technician from measuring resistance with an ohmmeter across airbag squibs "
            "or applying external test voltage. Warn that standard meter currents trigger accidental pyrotechnic deployment. "
            "Instruct that SRS disarming and service procedures must strictly follow OEM service manuals."
        )

    if triggers.get("ice_12v_battery_mismatch"):
        rules.append(
            "CRITICAL DOMAIN MISMATCH DIRECTIVE: The query is an ordinary 12V battery drain on an internal combustion engine (ICE) "
            "vehicle with an alternator. You MUST explicitly state that any retrieved EV/Hybrid high-voltage interlock codes "
            "(such as P0D17, P0D46, P0D23) are NOT applicable to this vehicle. Instruct standard 12V parasitic draw testing "
            "(fuse millivolt drop / inline ammeter check) instead."
        )

    if triggers.get("braking_hydraulic"):
        rules.append(
            "CRITICAL BRAKE SAFETY DIRECTIVE: A sinking brake pedal indicates internal master cylinder seal failure. "
            "You MUST state unequivocally that the vehicle is NOT SAFE TO DRIVE and must be towed to a repair facility. "
            "Never imply that the vehicle can be safely driven with a sinking pedal."
        )

    if triggers.get("cooling_thermal"):
        rules.append(
            "CRITICAL COOLING SAFETY DIRECTIVE: Warn never to open a hot, pressurized coolant reservoir cap due to explosive "
            "steam and scald burn hazards. Advise allowing the vehicle to cool down for at least 45 minutes."
        )

    if not rules:
        return ""

    return "\n\nACTIVE AUTOMOTIVE SAFETY DIRECTIVES FOR THIS QUERY:\n" + "\n".join(rules)
