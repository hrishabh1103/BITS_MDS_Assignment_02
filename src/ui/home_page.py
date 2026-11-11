"""Page 1: Home & System Overview Dashboard."""

import streamlit as st

from src.config import CHROMA_COLLECTION_NAME, DEFAULT_EMBEDDING_MODEL
from src.ui.components import get_cached_chroma_manager, get_cached_rag_pipeline


def render_home_page() -> None:
    """Renders the executive summary, system specs, and RAG architectural overview."""
    st.markdown('<div class="main-header">🚗 Vehicle Troubleshooting Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">'
        'BITS Pilani WILP — Modern Database Systems (Assignment 2) | Persistent ChromaDB & Grounded RAG Pipeline'
        '</div>',
        unsafe_allow_html=True,
    )

    chroma_mgr = get_cached_chroma_manager()
    record_count = chroma_mgr.get_count()
    rag = get_cached_rag_pipeline()
    gen_mode = getattr(rag.llm_provider, "generation_mode", "unknown")

    # Top KPI Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Indexed Diagnostic Records",
            value=f"{record_count:,}",
            help="Total verified vehicle troubleshooting records persisted in ChromaDB",
        )
    with col2:
        st.metric(
            label="Vector Embedding Model",
            value="384-dim",
            delta="all-MiniLM-L6-v2",
            delta_color="off",
            help="Normalized sentence-transformers embeddings in Cosine space",
        )
    with col3:
        st.metric(
            label="Language Model Provider",
            value="Llama 3.2 (3B)" if gen_mode == "real" else "Mock Fallback",
            delta="Ollama (Live)" if gen_mode == "real" else "Ollama Offline (Simulated)",
            delta_color="normal" if gen_mode == "real" else "off",
            help="Real Ollama Llama 3.2 local daemon or fallback MockLLMProvider",
        )
    with col4:
        st.metric(
            label="Evaluation Benchmark",
            value="10 Queries",
            delta="Q01 – Q10",
            delta_color="off",
            help="10 rigorous diagnostic queries covering 4 automotive subsystems",
        )

    st.markdown("---")

    # System Architecture and Overview Columns
    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.markdown("### 🎯 System Purpose & Academic Objective")
        st.write(
            """
            The **Vehicle Troubleshooting Assistant** is an end-to-end, knowledge-grounded diagnostic intelligence system. 
            It addresses the acute danger of unassisted Large Language Models (LLMs) hallucinating component replacements, 
            incorrect torque limits, or unsafe procedures on high-voltage and hydraulic braking vehicle systems.
            
            By decoupling dense semantic retrieval over a persistent **ChromaDB vector database** (9,532 records) from generative synthesis, 
            the assistant enforces strict factual grounding, in-text source attribution (`[VTR-XXXXX]`), and automated automotive safety guardrails.
            """
        )

        st.markdown("### 🛡️ Five Backend Automotive Safety Guardrails")
        st.markdown(
            """
            - **Supplemental Restraint Systems (SRS / Airbag)**: Strictly prohibits using an ohmmeter to measure squib resistance (pyrotechnic deployment hazard).
            - **High-Voltage Hybrid/EV Loops**: Warns against contacting orange 300V–800V cables and mandates Class-0 PPE and technician lockout/tagout.
            - **ICE 12V Battery Drain vs. EV Charger**: Catches domain mismatches where an ordinary alternator drain query retrieves high-voltage EV codes.
            - **Hydraulic Braking Failures**: Detects sinking brake pedals, mandates immediate towing, and forbids road driving.
            - **Thermal Cooling Scald Hazards**: Warns against opening pressurized, boiling coolant reservoirs.
            """
        )

    with col_right:
        st.markdown("### 🔄 How Retrieval-Augmented Generation (RAG) Operates")
        st.markdown(
            """
            ```mermaid
            flowchart TD
                A["1. Driver Symptom Input<br/>(Natural Language)"] --> B["2. Dense Embedding<br/>(all-MiniLM-L6-v2)"]
                B --> C[("3. ChromaDB Persistent KB<br/>(9,532 Diagnostic Records)")]
                C -->|Top-K Cosine Search| D["4. Relevant Context Injection<br/>(DTCs, Symptoms, Causes)"]
                D --> E["5. Safety Guardrail Engine<br/>(SRS, HV, Brakes, Thermal)"]
                E --> F["6. Grounded LLM Generation<br/>(Ollama Llama 3.2)"]
                F --> G["7. Structured Diagnostic Report<br/>(Citations, Checks, Limits)"]
            ```
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Bottom feature navigation callouts
    st.markdown("### 🧭 Interactive Application Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**🔧 Troubleshooting Assistant**\nEnter real-world driver symptoms, specify powertrain type (ICE/EV/Hybrid), and receive grounded diagnostic guidance.")
    with c2:
        st.info("**🔍 Semantic Search**\nExplore the 9,532 vector records, test metadata filters ($and logic), and inspect distance distributions.")
    with c3:
        st.info("**📊 Evaluation Dashboard**\nReview empirical benchmarks from Phase 4, Phase 5 (NumPy similarity comparison), and Phase 6.1 (Real LLM evaluation).")
    with c4:
        st.info("**📖 About & Dataset**\nInspect Zenodo / OBDex source attribution, preprocessing steps, category distributions, and known system limitations.")
