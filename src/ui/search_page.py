"""Page 3: Semantic Search & Metadata Filtering Explorer."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ui.components import (
    get_cached_search_engine,
    render_diagnostic_card,
    render_hero_header,
)


def render_search_page() -> None:
    """Renders the enhanced interactive dense vector search and metadata filtering interface."""
    render_hero_header(
        title="Semantic Vector Search Explorer",
        subtitle=(
            "Execute dense semantic queries across 9,532 vehicle diagnostic records in ChromaDB. "
            "Combines 384-dimensional cosine proximity with multi-condition metadata filtering."
        ),
        badge="ChromaDB Vector Retrieval Engine",
    )

    search_engine = get_cached_search_engine()

    # -------------------------------------------------------------
    # 1. QUICK QUERY CHIPS
    # -------------------------------------------------------------
    st.markdown("#### 💡 Quick Query Suggestions")
    suggestions = [
        "alternator charging normal but battery dead",
        "brake pedal sinks to floorboard ABS light",
        "engine misfire under load flashing check engine",
        "airbag warning light on after clock spring",
        "turbocharger sluggish acceleration severe lag",
    ]
    s_cols = st.columns(len(suggestions))
    for idx, s in enumerate(suggestions):
        if s_cols[idx].button(f"🔍 {s[:22]}...", key=f"sug_{idx}", help=s, use_container_width=True):
            st.session_state["search_query_input"] = s
            st.rerun()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. SEARCH CONTROLS
    # -------------------------------------------------------------
    col_q, col_opts = st.columns([1.6, 1.0])

    with col_q:
        default_search = st.session_state.get(
            "search_query_input",
            "alternator charging voltage normal but battery drains",
        )
        query_input = st.text_input(
            "Natural Language Technical Symptom or DTC Query:",
            value=default_search,
            placeholder="e.g. engine misfire under load, brake pedal sinks, CAN bus communication lost...",
            help="Queries are converted to 384-dimensional dense vectors and queried using Cosine distance.",
        )

    with col_opts:
        col_k, col_sys = st.columns(2)
        with col_k:
            top_k = st.slider("Result Cutoff ($K$):", min_value=1, max_value=25, value=5, step=1)
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
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div>
                    <h3 style="margin:0;">📋 Retrieved {len(results)} Matches for: <em>"{q}"</em></h3>
                    {f'<div style="font-size:0.85rem; color:#64748B; margin-top:0.2rem;">Active Filter: <code>{f}</code></div>' if f else ''}
                </div>
                <span class="metric-badge badge-system" style="font-size:0.9rem; padding:0.35rem 0.8rem;">
                    Top-{len(results)} of 9,532
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not results:
            st.info("No matching records found satisfying the query and filter criteria.")
            return

        # View Tabs: Card View vs. Tabular View vs. Similarity Chart
        tab_cards, tab_table, tab_chart = st.tabs([
            "🗂️ Diagnostic Cards View",
            "📊 Summary Data Table",
            "📈 Similarity Analytics Chart",
        ])

        with tab_cards:
            for idx, doc in enumerate(results, start=1):
                render_diagnostic_card(doc, rank=idx)

        with tab_table:
            table_records = []
            for idx, doc in enumerate(results, start=1):
                dist = doc.get("distance", 0.0)
                sim = doc.get("similarity_score", max(0.0, 1.0 - dist))
                table_records.append({
                    "Rank": idx,
                    "Record ID": doc.get("record_id"),
                    "DTC Code": doc.get("diagnostic_codes", "N/A"),
                    "Title": doc.get("title", ""),
                    "Subsystem": doc.get("vehicle_system", "").replace("_", " ").title(),
                    "Severity": doc.get("severity", "").upper(),
                    "Cosine Distance": round(dist, 4),
                    "Cosine Similarity": f"{sim * 100:.1f}%",
                })
            df_results = pd.DataFrame(table_records)
            st.dataframe(df_results, use_container_width=True, hide_index=True)

            csv_data = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Export Search Results to CSV",
                data=csv_data,
                file_name="semantic_search_results.csv",
                mime="text/csv",
            )

        with tab_chart:
            st.markdown("#### 📊 Cosine Similarity & Distance Distribution")
            chart_df = pd.DataFrame([
                {
                    "DTC Code": f"#{idx} {doc.get('diagnostic_codes', doc.get('record_id'))}",
                    "Cosine Similarity (%)": round(max(0.0, 1.0 - doc.get("distance", 0.0)) * 100, 1),
                    "Cosine Distance": round(doc.get("distance", 0.0), 4),
                    "Record": doc.get("title", ""),
                }
                for idx, doc in enumerate(results, start=1)
            ])
            fig = px.bar(
                chart_df,
                x="DTC Code",
                y="Cosine Similarity (%)",
                text="Cosine Similarity (%)",
                hover_data=["Record", "Cosine Distance"],
                color="Cosine Similarity (%)",
                color_continuous_scale="Blues",
                title=f"Retrieval Proximity for: '{q}'",
            )
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
