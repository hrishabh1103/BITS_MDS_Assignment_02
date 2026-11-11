"""Page 3: Semantic Search & Metadata Filtering Explorer."""

import pandas as pd
import streamlit as st

from src.ui.components import get_cached_search_engine, render_diagnostic_card


def render_search_page() -> None:
    """Renders the interactive dense vector search and metadata filtering interface."""
    st.markdown('<div class="main-header">🔍 Semantic Vector Search Explorer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">'
        'Execute dense semantic queries across 9,532 vehicle diagnostic records in ChromaDB with metadata filters.'
        '</div>',
        unsafe_allow_html=True,
    )

    search_engine = get_cached_search_engine()

    col_q, col_opts = st.columns([1.6, 1.0])

    with col_q:
        query_input = st.text_input(
            "Natural Language Query / Technical Problem:",
            value="alternator charging voltage normal but battery drains",
            placeholder="e.g. engine misfire under load, brake pedal sinks, CAN bus communication lost...",
            help="Queries are converted to 384-dimensional dense vectors and queried using Cosine distance.",
        )

    with col_opts:
        col_k, col_sys = st.columns(2)
        with col_k:
            top_k = st.slider("Result Limit ($K$):", min_value=1, max_value=25, value=5, step=1)
        with col_sys:
            subsystem_filter = st.selectbox(
                "Subsystem Filter:",
                options=["All Subsystems", "engine_and_transmission", "brakes_and_suspension", "electrical_and_body", "network_and_communication"],
                index=0,
            )

    col_sev, col_btn = st.columns([1.3, 1.0])
    with col_sev:
        severity_filter = st.selectbox(
            "Severity Filter:",
            options=["All Severities", "critical", "high", "medium", "low"],
            index=0,
        )
    with col_btn:
        st.write("")
        st.write("")
        search_clicked = st.button("🚀 Execute Semantic Search", type="primary", use_container_width=True)

    # Build ChromaDB filter dictionary if filters selected
    where_conditions = []
    if subsystem_filter != "All Subsystems":
        where_conditions.append({"vehicle_system": subsystem_filter})
    if severity_filter != "All Severities":
        where_conditions.append({"severity": severity_filter})

    where_filter = None
    if len(where_conditions) == 1:
        where_filter = where_conditions[0]
    elif len(where_conditions) > 1:
        where_filter = {"$and": where_conditions}

    if search_clicked or "last_search_results" in st.session_state:
        if search_clicked:
            if not query_input or not query_input.strip():
                st.warning("⚠️ Please provide a query to execute search.")
                return

            with st.spinner("Searching ChromaDB collection..."):
                results = search_engine.search(
                    query=query_input,
                    top_k=top_k,
                    where=where_filter,
                )
                st.session_state["last_search_results"] = results
                st.session_state["last_search_query"] = query_input
                st.session_state["last_search_filter"] = where_filter

        results = st.session_state.get("last_search_results", [])
        q = st.session_state.get("last_search_query", "")
        f = st.session_state.get("last_search_filter", None)

        st.markdown("---")
        st.markdown(f"### 📋 Retrieved {len(results)} Records for: *\"{q}\"*")
        if f:
            st.caption(f"Active ChromaDB Filter: `{f}`")

        if not results:
            st.info("No matching records found satisfying the query and filter criteria.")
            return

        # View Tabs: Card View vs. Tabular View
        tab_cards, tab_table = st.tabs(["🗂️ Diagnostic Cards View", "📊 Summary Data Table"])

        with tab_cards:
            for idx, doc in enumerate(results, start=1):
                render_diagnostic_card(doc, rank=idx)
                with st.expander(f"Inspect Full Diagnostic Text for {doc.get('record_id')}", expanded=False):
                    st.text(doc.get("document", "N/A"))

        with tab_table:
            table_rows = []
            for idx, r in enumerate(results, start=1):
                table_rows.append({
                    "Rank": idx,
                    "Record ID": r.get("record_id"),
                    "Diagnostic Code": r.get("diagnostic_codes"),
                    "Subsystem": r.get("vehicle_system"),
                    "Severity": r.get("severity"),
                    "Cosine Distance": round(r.get("distance", 0.0), 4),
                    "Cosine Similarity": round(r.get("similarity_score", 0.0), 4),
                    "Title": r.get("title"),
                })
            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
