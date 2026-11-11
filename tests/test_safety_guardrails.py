"""Unit and integration tests for backend automotive safety guardrails and evaluation bug fixes.

Tests:
1. SRS / Airbag safety detection & prohibition of ohmmeter squib checks.
2. Non-SRS B-codes do NOT trigger false airbag guardrails.
3. High-Voltage EV/Hybrid shock hazard warnings.
4. ICE 12V battery drain vs. EV charger domain mismatch detection.
5. Hydraulic braking failure warnings (sinking pedal -> do not drive).
6. Cooling system scald hazard warnings (hot pressurized coolant).
7. Safety keyword false-positive prevention (words like 'based', 'case', 'causes' do not trigger false safety flags).
8. Configurable token generation and truncation detection.
9. Provider error and graceful fallback handling.
"""

import pytest
from src.llm_provider import LLMResponse, MockLLMProvider
from src.rag_evaluation import evaluate_safety_and_structure
from src.rag_pipeline import RAGPipeline
from src.safety_guardrails import (
    build_safety_augmented_instructions,
    detect_safety_triggers,
    generate_safety_alerts,
)


def test_safety_keyword_false_positives_prevented():
    """Verifies that common words like 'based', 'causes', and 'case' do NOT trigger false safety flags."""
    # Text with ordinary automotive prose containing substrings of 'ase'
    ordinary_text = (
        "Based on the retrieved context, the probable causes of engine hesitation "
        "include a case of dirty fuel injectors or an intake air leak in phase one."
    )
    eval_res = evaluate_safety_and_structure(ordinary_text)
    assert eval_res["has_safety_disclaimer"] is False, (
        "False positive detected! Substrings 'based' or 'causes' falsely triggered safety flag."
    )

    # Text with actual safety warning
    safety_text = (
        "Safety warning: High voltage components carry lethal shock hazards. "
        "Repairs must be performed by an ASE-certified technician wearing Class 0 gloves."
    )
    eval_safety = evaluate_safety_and_structure(safety_text)
    assert eval_safety["has_safety_disclaimer"] is True


def test_srs_airbag_safety_guardrail():
    """Verifies SRS/airbag query detection and strict ohmmeter squib warnings."""
    query = "Supplemental restraint system airbag light stays on after clock spring replacement"
    docs = [
        {"title": "DTC B0005 - Steering Column Deployment Control", "diagnostic_codes": "B0005", "document": "Driver frontal stage 1 deployment squib loop"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs)
    assert triggers["srs_airbag"] is True

    alerts = generate_safety_alerts(triggers)
    srs_alerts = [a for a in alerts if a.category == "SRS_AIRBAG"]
    assert len(srs_alerts) == 1
    alert = srs_alerts[0]
    assert alert.severity == "DANGER"
    assert "ohmmeter" in alert.message.lower()
    assert "pyrotechnic" in alert.message.lower()

    instructions = build_safety_augmented_instructions(triggers)
    assert "CRITICAL SRS/AIRBAG DIRECTIVE" in instructions
    assert "forbid" in instructions.lower() or "never" in instructions.lower()


def test_generic_b_code_does_not_trigger_srs_rule():
    """Verifies requirement: do not trigger SRS airbag rule merely because a record has a B-code."""
    query = "Power window switch unresponsive on driver door"
    # Generic body code (e.g. B1000 - ECU Malfunction or B0223 - HVAC air flow) without airbag terms
    docs = [
        {"title": "DTC B0223 - HVAC Air Flow Control Circuit", "diagnostic_codes": "B0223", "document": "Actuator circuit failure in climate control blend door"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs)
    assert triggers["srs_airbag"] is False, "SRS rule triggered falsely on a non-airbag B-code!"


def test_high_voltage_ev_safety_guardrail():
    """Verifies detection of EV high-voltage loops and 400V shock hazard warnings."""
    query = "Hybrid vehicle traction inverter shuts down with high voltage interlock error"
    docs = [
        {"title": "DTC P0D17 - High Voltage Interlock Circuit Low", "diagnostic_codes": "P0D17", "document": "HVIL loop open or shorted to ground"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs, vehicle_type="Hybrid")
    assert triggers["high_voltage_ev"] is True

    alerts = generate_safety_alerts(triggers)
    hv_alerts = [a for a in alerts if a.category == "HIGH_VOLTAGE_EV"]
    assert len(hv_alerts) == 1
    assert hv_alerts[0].severity == "DANGER"
    assert "orange" in hv_alerts[0].message.lower()


def test_ice_12v_battery_drain_vs_ev_mismatch():
    """Verifies that EV charger/HVIL records retrieved for an ICE 12V battery drain trigger domain mismatch."""
    query = "Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle"
    # Retrieved docs containing EV charger codes
    docs = [
        {"title": "DTC P0D17 - High Voltage Interlock Circuit Low", "diagnostic_codes": "P0D17", "document": "High voltage interlock open"},
        {"title": "DTC P0D46 - Battery Charger 14 V Output Sensor", "diagnostic_codes": "P0D46", "document": "Onboard charger sensor failure"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs, vehicle_type="ICE")
    assert triggers["ice_12v_battery_mismatch"] is True

    alerts = generate_safety_alerts(triggers)
    mismatch_alerts = [a for a in alerts if a.category == "DOMAIN_MISMATCH"]
    assert len(mismatch_alerts) == 1
    assert "MISMATCH" in mismatch_alerts[0].title
    assert "parasitic draw" in mismatch_alerts[0].recommended_action.lower()


def test_braking_hydraulic_safety_guardrail():
    """Verifies sinking brake pedal triggers critical hazard warning and do-not-drive directive."""
    query = "Brake pedal sinks slowly to the floorboard at red lights"
    docs = [
        {"title": "DTC C0291 - Brake Pedal Apply Sensor", "diagnostic_codes": "C0291", "document": "Pedal position sensor circuit performance"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs)
    assert triggers["braking_hydraulic"] is True

    alerts = generate_safety_alerts(triggers)
    brake_alerts = [a for a in alerts if a.category == "BRAKING_HAZARD"]
    assert len(brake_alerts) == 1
    assert brake_alerts[0].severity == "CRITICAL"
    assert "DO NOT DRIVE" in brake_alerts[0].title
    assert "towed" in brake_alerts[0].recommended_action.lower()


def test_cooling_system_scald_guardrail():
    """Verifies overheating coolant queries trigger scald hazard warning."""
    query = "Engine overheating rapidly with boiling coolant in reservoir"
    docs = [
        {"title": "DTC P00B7 - Coolant Flow Low", "diagnostic_codes": "P00B7", "document": "Engine overheating temperature threshold exceeded"},
    ]
    triggers = detect_safety_triggers(query=query, retrieved_docs=docs)
    assert triggers["cooling_thermal"] is True

    alerts = generate_safety_alerts(triggers)
    thermal_alerts = [a for a in alerts if a.category == "THERMAL_SCALD"]
    assert len(thermal_alerts) == 1
    assert "SCALD HAZARD" in thermal_alerts[0].title


def test_truncation_detection_and_handling():
    """Verifies that hitting the max_tokens limit flags execution_status='truncated'."""
    # Create mock provider that generates more tokens than a tight limit
    class LongOutputMockProvider(MockLLMProvider):
        def generate(self, prompt, system_prompt=None, temperature=0.2, max_tokens=10):
            return LLMResponse(
                content="Long diagnostic content that exceeds the maximum output token limit...",
                model_name="mock",
                provider_name="mock",
                generation_mode="mock",
                latency_ms=10.0,
                tokens_used={"completion_tokens": 10, "prompt_tokens": 20, "total_tokens": 30},
            )

    pipeline = RAGPipeline(llm_provider=LongOutputMockProvider())
    res = pipeline.query("test query", max_tokens=10)
    assert res["is_truncated"] is True
    assert res["execution_status"] == "truncated"


def test_provider_error_handling():
    """Verifies graceful handling when the LLM provider fails."""
    class FailingMockProvider(MockLLMProvider):
        def generate(self, prompt, system_prompt=None, temperature=0.2, max_tokens=1024):
            return LLMResponse(
                content="",
                model_name="mock",
                provider_name="mock",
                generation_mode="mock",
                latency_ms=5.0,
                error="Simulated network failure / API timeout",
            )

    pipeline = RAGPipeline(llm_provider=FailingMockProvider())
    res = pipeline.query("test query")
    assert res["execution_status"] == "failed"
    assert "Simulated network failure" in res["error_message"]


def test_airbag_battery_disconnection_not_sufficient_alone():
    """Verifies requirement: battery disconnect is NOT presented as sufficient by itself to make SRS safe."""
    triggers = {"srs_airbag": True}
    alerts = generate_safety_alerts(triggers)
    srs_alerts = [a for a in alerts if a.category == "SRS_AIRBAG"]
    assert len(srs_alerts) == 1
    action = srs_alerts[0].recommended_action
    assert "not sufficient by itself" in action.lower() or "not sufficient" in action.lower()
    assert "ase-certified" in action.lower()
    assert "dummy load" in action.lower() or "certified" in action.lower()


def test_high_voltage_class0_gloves_alone_not_sufficient():
    """Verifies requirement: Class-0 gloves alone do NOT make high-voltage work safe, and unqualified users are not encouraged."""
    triggers = {"high_voltage_ev": True, "ice_12v_battery_mismatch": False}
    alerts = generate_safety_alerts(triggers)
    hv_alerts = [a for a in alerts if a.category == "HIGH_VOLTAGE_EV"]
    assert len(hv_alerts) == 1
    msg = hv_alerts[0].message
    assert "does not make high-voltage work safe" in msg.lower() or "not make high-voltage work safe" in msg.lower()
    action = hv_alerts[0].recommended_action
    assert "do not attempt diy" in action.lower() or "exclusively to certified" in action.lower()


def test_cooling_warning_no_arbitrary_45min_period():
    """Verifies requirement: cooling warnings do NOT prescribe an arbitrary universal 45-minute waiting period."""
    triggers = {"cooling_thermal": True}
    alerts = generate_safety_alerts(triggers)
    thermal_alerts = [a for a in alerts if a.category == "THERMAL_SCALD"]
    assert len(thermal_alerts) == 1
    action = thermal_alerts[0].recommended_action
    assert "do not rely on an arbitrary" in action.lower()
    assert "cold to the touch" in action.lower()
    assert "zero" in action.lower() and "pressure" in action.lower()


def test_false_positive_catalytic_and_torque_converter():
    """Verifies that words like 'catalytic converter' or 'torque converter' do NOT trigger high-voltage EV alerts."""
    cat_query = "Check engine light on with DTC P0420 catalytic converter system efficiency below threshold"
    triggers_cat = detect_safety_triggers(query=cat_query, retrieved_docs=[])
    assert triggers_cat["high_voltage_ev"] is False, "High voltage EV triggered falsely on catalytic converter!"

    tc_query = "Automatic transmission exhibits torque converter clutch slip at highway cruising speeds"
    triggers_tc = detect_safety_triggers(query=tc_query, retrieved_docs=[])
    assert triggers_tc["high_voltage_ev"] is False, "High voltage EV triggered falsely on torque converter!"


def test_false_positive_washer_fluid_and_ac_floorboard():
    """Verifies that non-brake fluids and floorboard water leaks do NOT trigger brake failure alerts."""
    washer_query = "Windshield washer fluid leak under front bumper after topping off fluid reservoir"
    triggers_washer = detect_safety_triggers(query=washer_query, retrieved_docs=[])
    assert triggers_washer["braking_hydraulic"] is False, "Brake failure triggered falsely on washer fluid leak!"

    floorboard_query = "Water pooling on passenger floorboard carpet due to clogged air conditioning evaporator drain"
    triggers_floor = detect_safety_triggers(query=floorboard_query, retrieved_docs=[])
    assert triggers_floor["braking_hydraulic"] is False, "Brake failure triggered falsely on AC drain floorboard leak!"


def test_ordinary_unrelated_queries_produce_zero_safety_alerts():
    """Verifies that clean everyday vehicle queries produce zero active safety alerts."""
    unrelated_queries = [
        "Tire pressure monitoring system TPMS light flashing after seasonal wheel change",
        "Engine misfire at idle with DTC P0300 random multiple cylinder misfire",
        "Vehicle pull to the right during straight line cruising due to wheel alignment",
    ]
    for q in unrelated_queries:
        triggers = detect_safety_triggers(query=q, retrieved_docs=[])
        alerts = generate_safety_alerts(triggers)
        assert len(alerts) == 0, f"False safety alert generated for ordinary query: '{q}'"
