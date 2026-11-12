"""Page 2: Vehicle Troubleshooting Assistant (Grounded RAG & Safety Engine)."""

import json
from typing import Any, Dict
import streamlit as st

from src.config import QUERIES_FILE
from src.ui.components import (
    get_cached_rag_pipeline,
    render_diagnostic_card,
    render_hero_header,
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
    """Renders the enhanced interactive AI troubleshooting assistant interface."""
    render_hero_header(
        title="Vehicle Troubleshooting Assistant",
        subtitle=(
            "Execute domain-grounded diagnostic analysis over 9,532 persistent ChromaDB records. "
            "Features automated citation attribution [VTR-XXXXX], anti-hallucination guardrails, and active shop-safety interceptors."
        ),
        badge="Grounded RAG & Safety Validation Engine",
    )

    preset_map = load_preset_queries()

    # -------------------------------------------------------------
    # 1. QUICK DEMO PRESET CHIPS
    # -------------------------------------------------------------
    st.markdown("#### ⚡ Quick Demo Presets (Select a Benchmark Diagnostic Query)")
    
    preset_items = list(preset_map.items())[:5]
    preset_icons = ["❄️", "⚡", "🛑", "🎈", "🏎️"]
    cols = st.columns(len(preset_items))
    for idx, (label, query_val) in enumerate(preset_items):
        icon = preset_icons[idx % len(preset_icons)]
        short_label = f"{icon} {label.split(':')[0]}"
        tooltip = f"{label}: {query_val}"
        if cols[idx].button(short_label, key=f"btn_preset_{idx}", help=tooltip, use_container_width=True):
            st.session_state["query_input"] = query_val
            st.rerun()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. INPUT FORM
    # -------------------------------------------------------------
    with st.form("troubleshooting_form"):
        col_main, col_side = st.columns([1.6, 1.0])

        with col_main:
            default_query = st.session_state.get(
                "query_input",
                "Brake pedal sinks slowly to the floorboard at red lights with ABS warning light illuminated on dashboard",
            )
            query_text = st.text_area(
                "Describe Vehicle Symptoms, Driver Complaint, or Observed DTC Codes:",
                value=default_query,
                height=120,
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
            top_k = st.slider("Retrieval Cutoff ($K$):", min_value=1, max_value=10, value=5, step=1, help="Number of nearest-neighbor records to retrieve from ChromaDB")
        with col_tokens:
            max_tokens = st.slider("Max Output Tokens:", min_value=512, max_value=2048, value=1536, step=256, help="Cap to prevent output truncation while maintaining generation safety")
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

    # -------------------------------------------------------------
    # 3. RESULTS DISPLAY
    # -------------------------------------------------------------
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
                "⚠️ **Context Domain Mismatch Intercepted**: The query describes an ICE 12V electrical system, "
                "but retrieved records involve High-Voltage EV/Hybrid charging systems. The backend safety engine "
                "has injected directives instructing standard 12V parasitic draw millivolt testing."
            )

        # 3. Provider Availability and Simulation Notice
        if res.get("generation_mode") == "mock":
            st.warning(
                "⚠️ **Ollama Local Service Unavailable — Simulated Response Active**: "
                "The local Ollama server is not reachable on localhost:11434. "
                "This response was generated using **MockLLMProvider** for offline demonstration. "
                "Mock outputs are deterministic simulations and are NEVER silently presented as live LLM inference."
            )
        elif res.get("generation_mode") == "real":
            st.success(
                f"✅ **Live LLM Output**: Generated via `{res.get('llm_provider')}` "
                f"using model `{res.get('llm_model')}` on local hardware."
            )

        # 4. Truncation Disclaimer
        if res.get("is_truncated"):
            st.error(
                f"⚠️ **Response Truncated**: Model output reached configured limit ({max_tokens} tokens). "
                "Increase 'Max Output Tokens' in the input form if needed."
            )

        col_ans, col_ctx = st.columns([1.35, 0.9])

        with col_ans:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <h3 style="margin:0;">🤖 Grounded Diagnostic Report</h3>
                    <span style="font-size:0.8rem; background:#F1F5F9; padding:0.25rem 0.6rem; border-radius:6px; font-family:monospace; color:#334155;">
                        ⏱️ Latency: {res.get('latency_ms', 0):.0f} ms
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Diagnostic Report Body Container
            st.markdown(
                f"""
                <div class="report-container">
                    <div class="report-header">
                        <div>
                            <strong>Provider:</strong> <code>{res.get('llm_provider')}</code> | 
                            <strong>Model:</strong> <code>{res.get('llm_model')}</code>
                        </div>
                        <div>
                            <span class="metric-badge badge-system">Mode: {res.get('generation_mode', '').upper()}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display Answer Text
            st.markdown(res.get("generated_answer", "No answer generated."))

            # Cited record pill badges
            cited = res.get("source_record_ids", [])
            st.markdown("#### 📑 Verified Source Record Citations")
            if cited:
                pill_html = " ".join([
                    f"<span style='background-color:#DBEAFE; color:#1E40AF; padding:0.25rem 0.65rem; "
                    f"border-radius:6px; font-family:monospace; font-weight:700; border:1px solid #BFDBFE;'>[{c}]</span>"
                    for c in cited
                ])
                st.markdown(pill_html, unsafe_allow_html=True)
            else:
                st.write("*No direct record citations identified in output.*")

            # Download Diagnosis Summary Button
            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            report_text = f"# Vehicle Diagnostic Report\n\n**Query:** {query_text}\n**Vehicle:** {vehicle_type}\n**Latency:** {res.get('latency_ms', 0):.0f} ms\n\n## Grounded Diagnosis\n\n{res.get('generated_answer', '')}\n\n## Verified Citations\n\n{', '.join(cited)}"
            st.download_button(
                label="📥 Download Diagnostic Report (.md)",
                data=report_text,
                file_name="vehicle_diagnostic_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_ctx:
            st.markdown(f"### 📚 Retrieved Context ({len(res.get('retrieved_documents', []))} Records)")
            st.caption("Top nearest-neighbor matches from persistent collection `vehicle_troubleshooting_kb`:")

            for doc in res.get("retrieved_documents", []):
                render_diagnostic_card(doc, rank=doc.get("rank", 1))
                with st.expander(f"🔍 Inspect Full Record {doc.get('record_id')}", expanded=False):
                    st.text(doc.get("excerpt", doc.get("document", "N/A")))
