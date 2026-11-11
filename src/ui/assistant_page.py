"""Page 2: Vehicle Troubleshooting Assistant (Grounded RAG & Safety Engine)."""

import json
from typing import Any, Dict
import streamlit as st

from src.config import QUERIES_FILE
from src.ui.components import (
    get_cached_rag_pipeline,
    render_diagnostic_card,
    render_safety_alerts,
)


def load_preset_queries() -> Dict[str, str]:
    """Loads assignment preset queries for one-click demonstration."""
    try:
        with open(QUERIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {f"{q['query_id']}: {q['topic']}": q["query_text"] for q in data}
    except Exception:
        return {
            "Q01: Cooling Overheat": "Engine overheating rapidly at highway speeds with boiling coolant in reservoir",
            "Q03: Battery Drain": "Vehicle battery goes completely dead overnight with alternator charging voltage testing normal during idle",
            "Q04: Sinking Brake": "Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated",
            "Q09: Airbag Warning": "Supplemental restraint system airbag warning light stays on continuously after replacing steering column clock spring",
            "Q10: Turbo Lag": "Turbocharged vehicle exhibits sluggish acceleration, severe turbo lag, and underboost condition when climbing hills",
        }


def render_assistant_page() -> None:
    """Renders the interactive AI troubleshooting assistant interface."""
    st.markdown('<div class="main-header">🔧 Vehicle Troubleshooting Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">'
        'Query the 9,532-record ChromaDB knowledge base with grounded retrieval, in-text citations, and automotive safety guardrails.'
        '</div>',
        unsafe_allow_html=True,
    )

    preset_map = load_preset_queries()

    # Form inputs
    with st.expander("⚡ Quick Demo Presets (Assignment Benchmark Queries)", expanded=False):
        preset_cols = st.columns(len(preset_map) if len(preset_map) <= 5 else 5)
        for idx, (label, text) in enumerate(list(preset_map.items())[:5]):
            col = preset_cols[idx % 5]
            if col.button(label.split(":")[0], key=f"preset_{idx}", help=label):
                st.session_state["query_input"] = text

    with st.form("troubleshooting_form"):
        col_main, col_side = st.columns([1.6, 1.0])

        with col_main:
            default_query = st.session_state.get(
                "query_input",
                "Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard",
            )
            query_text = st.text_area(
                "Describe the Vehicle Problem / Symptom:",
                value=default_query,
                height=110,
                placeholder="e.g. Engine overheating rapidly at highway speeds with boiling coolant in reservoir...",
                help="Enter natural language driver complaints, symptoms, or observed DTC codes.",
            )

        with col_side:
            vehicle_type = st.selectbox(
                "Vehicle Powertrain Type:",
                options=["ICE", "Hybrid", "EV", "Unknown"],
                index=0,
                help="Helps the backend safety engine detect 12V ICE vs. High-Voltage EV domain mismatches.",
            )
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                make = st.text_input("Make (optional):", placeholder="e.g. Ford / Honda")
                year = st.text_input("Year (optional):", placeholder="e.g. 2018")
            with col_v2:
                model = st.text_input("Model (optional):", placeholder="e.g. F-150 / Civic")
                engine = st.text_input("Engine / Code (optional):", placeholder="e.g. 3.5L EcoBoost")

        col_k, col_tokens, col_btn = st.columns([1, 1, 1])
        with col_k:
            top_k = st.slider("Retrieval Cutoff ($K$):", min_value=1, max_value=10, value=5, step=1)
        with col_tokens:
            max_tokens = st.slider("Max Output Tokens:", min_value=512, max_value=2048, value=1536, step=256)
        with col_btn:
            st.write("")
            st.write("")
            submitted = st.form_submit_button("🔍 Diagnose Vehicle Problem", type="primary", use_container_width=True)

    if submitted:
        if not query_text or not query_text.strip():
            st.error("⚠️ Please enter a symptom or vehicle problem description before submitting.")
            return

        vehicle_info = {
            "make": make.strip() if make else "",
            "model": model.strip() if model else "",
            "year": year.strip() if year else "",
            "engine": engine.strip() if engine else "",
        }

        pipeline = get_cached_rag_pipeline()

        with st.spinner(f"Retrieving top-{top_k} records from ChromaDB and generating grounded diagnosis..."):
            result = pipeline.query(
                query_text=query_text,
                top_k=top_k,
                vehicle_type=vehicle_type,
                vehicle_info=vehicle_info,
                max_tokens=max_tokens,
            )

        st.session_state["last_result"] = result

    # Display Results if available
    if "last_result" in st.session_state:
        res = st.session_state["last_result"]

        st.markdown("---")

        # 1. Prominent Safety Alerts Banner
        safety_alerts = res.get("safety_alerts", [])
        if safety_alerts:
            render_safety_alerts(safety_alerts)

        # 2. Context Mismatch Banner (ICE 12V vs EV records)
        if res.get("context_mismatch"):
            st.warning(
                "⚠️ **Context Domain Mismatch Notice**: The query describes an ICE 12V electrical system, "
                "but retrieved records involve High-Voltage EV/Hybrid charging systems. The response has been "
                "guarded against incorrectly attributing 12V issues to EV high-voltage loops."
            )

        # 3. Truncation Disclaimer
        if res.get("is_truncated"):
            st.error(
                f"⚠️ **Response Truncated**: Model output reached the configured token limit ({max_tokens} tokens). "
                "Portions of the diagnostic procedures or limitations section may be cut off. "
                "Increase 'Max Output Tokens' in the input form if needed."
            )

        col_ans, col_ctx = st.columns([1.3, 0.9])

        with col_ans:
            st.markdown("### 🤖 Grounded Diagnostic Analysis")
            st.markdown(
                f"<div style='font-size:0.85rem; color:#6B7280; margin-bottom:0.75rem;'>"
                f"Provider: <code>{res.get('llm_provider')}</code> | Model: <code>{res.get('llm_model')}</code> | "
                f"Mode: <code>{res.get('generation_mode', '').upper()}</code> | "
                f"Latency: <code>{res.get('latency_ms', 0):.0f} ms</code>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Display Answer Text
            st.markdown(res.get("generated_answer", "No answer generated."))

            # Cited record pill badges
            cited = res.get("source_record_ids", [])
            st.markdown("#### 📑 Verified Source Record Citations")
            if cited:
                pill_html = " ".join([
                    f"<span style='background-color:#DBEAFE; color:#1E40AF; padding:0.2rem 0.5rem; "
                    f"border-radius:4px; font-family:monospace; font-weight:600;'>[{c}]</span>"
                    for c in cited
                ])
                st.markdown(pill_html, unsafe_allow_html=True)
            else:
                st.write("*No direct record citations identified in output.*")

        with col_ctx:
            st.markdown(f"### 📚 Retrieved Context ({len(res.get('retrieved_documents', []))} Records)")
            st.markdown(
                "<div style='font-size:0.85rem; color:#6B7280; margin-bottom:0.75rem;'>"
                "Dense vector matches retrieved from persistent ChromaDB collection <code>vehicle_troubleshooting_kb</code>."
                "</div>",
                unsafe_allow_html=True,
            )

            for doc in res.get("retrieved_documents", []):
                render_diagnostic_card(doc, rank=doc.get("rank", 1))
                with st.expander(f"Full Diagnostic Text for {doc.get('record_id')}", expanded=False):
                    st.text(doc.get("excerpt", doc.get("document", "N/A")))
