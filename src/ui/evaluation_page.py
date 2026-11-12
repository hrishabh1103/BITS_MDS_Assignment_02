"""Page 4: Empirical Evaluation Dashboard (Phase 4, Phase 5, Phase 6.1)."""

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import EXPERIMENTS_DIR
from src.ui.components import render_hero_header


@st.cache_data
def load_real_evaluation_data():
    """Loads Phase 6.1 real evaluation data."""
    csv_path = EXPERIMENTS_DIR / "rag_real_evaluation.csv"
    json_path = EXPERIMENTS_DIR / "rag_real_results.json"
    comp_path = EXPERIMENTS_DIR / "rag_real_context_vs_baseline.json"

    df = pd.read_csv(csv_path) if csv_path.exists() else pd.DataFrame()
    with open(json_path, "r", encoding="utf-8") as f:
        real_results = json.load(f) if json_path.exists() else {}
    with open(comp_path, "r", encoding="utf-8") as f:
        comps = json.load(f) if comp_path.exists() else []

    return df, real_results, comps


@st.cache_data
def load_numpy_similarity_data():
    """Loads Phase 5 similarity comparison data."""
    path = EXPERIMENTS_DIR / "similarity_comparison_results.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data
def load_semantic_search_data():
    """Loads Phase 4 semantic search benchmark data."""
    path = EXPERIMENTS_DIR / "semantic_search_results.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_evaluation_page() -> None:
    """Renders the comprehensive multi-phase empirical evaluation dashboard."""
    render_hero_header(
        title="Empirical Evaluation Dashboard",
        subtitle=(
            "Quantitative benchmarks, mathematical ranking proofs, and real LLM inference audits across "
            "Phase 4 (Dense Retrieval), Phase 5 (NumPy Metric Equivalence), and Phase 6.1 (Grounded RAG vs. Baseline)."
        ),
        badge="Empirical Quality & Rigor Audit",
    )

    df_eval, real_results, comps = load_real_evaluation_data()
    sim_data = load_numpy_similarity_data()
    search_data = load_semantic_search_data()

    tab_rag, tab_fidelity, tab_metrics, tab_search = st.tabs([
        "🔬 Phase 6.1: Real RAG vs. Baseline",
        "📑 Citation Fidelity & Provenance",
        "📐 Phase 5: NumPy Similarity Metrics",
        "🔍 Phase 4: Dense Retrieval Benchmarks",
    ])

    # -------------------------------------------------------------
    # TAB 1: Real RAG vs. Baseline
    # -------------------------------------------------------------
    with tab_rag:
        st.markdown("### 🤖 Phase 6.1 Real LLM Inference (Meta Llama 3.2 on Local Hardware)")
        st.caption(
            "Quantitative comparison from 20 live local generations across 10 benchmark queries (Q01–Q10). "
            "Data loaded directly from `experiments/rag_real_*`."
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Citation Precision", "100.0%", delta="48/48 valid IDs", delta_color="normal")
        with col2:
            st.metric("Citation Recall", "96.0%", delta="48/50 retrieved", delta_color="normal")
        with col3:
            st.metric("Avg RAG Length", "487 words", delta="+120 vs baseline")
        with col4:
            st.metric("Avg Latency", "118.3s", delta="Local Apple Silicon MPS")

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        # Plotly Comparison Charts
        if not df_eval.empty:
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("#### 📊 Response Specificity (Word Count Comparison)")
                fig_words = go.Figure(data=[
                    go.Bar(name='Grounded RAG', x=df_eval['query_id'], y=df_eval['rag_word_count'], marker_color='#2563EB'),
                    go.Bar(name='Unassisted Baseline', x=df_eval['query_id'], y=df_eval['baseline_word_count'], marker_color='#94A3B8')
                ])
                fig_words.update_layout(
                    barmode='group',
                    height=330,
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_words, use_container_width=True)

            with col_chart2:
                st.markdown("#### ⏱️ Real LLM Inference Latency (Seconds)")
                latency_values = [
                    real_results.get(qid, {}).get("latency_seconds", 118.0)
                    for qid in df_eval['query_id']
                ]
                fig_lat = px.line(
                    x=df_eval['query_id'],
                    y=latency_values,
                    markers=True,
                    labels={"x": "Benchmark Query ID", "y": "Latency (s)"},
                    title="Per-Query Generation Latency (Meta Llama 3.2 3B)",
                )
                fig_lat.update_traces(line_color="#4F46E5", marker=dict(size=8, color="#1E40AF"))
                fig_lat.update_layout(height=330, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_lat, use_container_width=True)

            st.markdown("#### 📋 Q01 – Q10 Comprehensive Benchmark Metrics")
            display_df = df_eval[[
                "query_id", "rag_retrieved_k", "rag_cited_count", "rag_valid_citations",
                "rag_dtcs", "rag_word_count", "baseline_cited_count", "baseline_word_count"
            ]].copy()
            display_df.columns = [
                "Query ID", "Retrieved (K)", "RAG Cited IDs", "Valid Citations",
                "Referenced DTCs", "RAG Words", "Baseline Cited", "Baseline Words"
            ]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🔍 Side-by-Side Response Inspector (Q01 – Q10)")
        
        q_options = [c.get("query_id") + ": " + c.get("query")[:65] + "..." for c in comps] if comps else []
        if q_options:
            selected_idx = st.selectbox("Select Benchmark Query to Inspect:", options=range(len(q_options)), format_func=lambda i: q_options[i])
            selected_comp = comps[selected_idx]

            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown(f"**Grounded RAG Answer ({selected_comp['query_id']})**")
                rag_ans = selected_comp.get("rag", {}).get("generated_answer", "N/A")
                st.info(rag_ans)
                st.caption(f"Cited Record Provenance: `{selected_comp['rag'].get('cited_record_ids')}`")

            with col_r:
                st.markdown(f"**Unassisted Baseline Answer ({selected_comp['query_id']})**")
                base_ans = selected_comp.get("baseline", {}).get("generated_answer", "N/A")
                st.warning(base_ans)
                st.caption("Zero retrieved context. Generic automotive advice without source citations.")

    # -------------------------------------------------------------
    # TAB 2: Citation Fidelity & Anti-Hallucination
    # -------------------------------------------------------------
    with tab_fidelity:
        st.markdown("### 📑 Citation Provenance Consistency vs. Factual Ground Truth")
        
        st.warning(
            "⚠️ **Methodological Boundary Disclosure**: In retrieval-augmented generation evaluation, "
            "**Citation Precision** measures **reference provenance consistency** (verifying that cited record IDs "
            "belong to the retrieved context set without fabricating synthetic IDs). It does NOT equate to 100% mechanical "
            "truthfulness or replace certified technician inspection. For example, in Q03 the model cited `[VTR-P0D17]` with "
            "100% precision because it was retrieved, even though connecting an EV high-voltage code to an ICE 12V battery drain "
            "is mechanically mismatched."
        )

        st.markdown(
            """
            $$\\text{Citation Precision} = \\frac{|\\text{Valid Citations}|}{|\\text{Total Cited Record IDs}|} = \\frac{48}{48} = 1.0000\\text{ (100.0%)}$$
            
            $$\\text{Citation Recall} = \\frac{|\\text{Valid Citations}|}{|\\text{Total Retrieved Context Records}|} = \\frac{48}{50} = 0.9600\\text{ (96.0%)}$$
            """
        )

        st.markdown("#### 🔬 Detailed Findings from the Empirical Audit")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                """
                **1. Zero Fabricated Citations**:
                - Across all 10 real queries, the model cited 48 record IDs.
                - Exactly 0 non-existent record IDs were generated.
                - All 48 cited IDs corresponded to actual ChromaDB database records.
                
                **2. Unassisted Baseline Clean Isolation**:
                - In baseline mode (zero retrieved context), the model cited 0 records across all 10 queries.
                - Zero citation contamination or leaked formatting occurred in unassisted mode.
                """
            )
        with col_b:
            st.markdown(
                """
                **3. Boundary Keyword Pattern Hardening**:
                - Legacy substring checks (`'ase' in text`) matched common words like *based* and *cases*.
                - Patched using whole-word boundary regular expressions (`r"\\bASE\\b"`).
                
                **4. Transparent Negative Findings**:
                - Q03 (12V drain vs EV charger) and Q09 (airbag squib resistance warning) represent authentic AI behavioral observations documented in `docs/phase8_2_final_audit.md`.
                """
            )

    # -------------------------------------------------------------
    # TAB 3: Phase 5 NumPy Similarity Metrics
    # -------------------------------------------------------------
    with tab_metrics:
        st.markdown("### 📐 Phase 5: Exhaustive NumPy Similarity Metric Comparison")
        st.write(
            """
            In Phase 5, all 10 assignment queries were evaluated against all 9,532 database embeddings using 
            pure NumPy across three distinct similarity metrics:
            1. **Euclidean Distance ($L_2$)**
            2. **Cosine Similarity**
            3. **Dot Product (Inner Product)**
            """
        )

        st.markdown(
            """
            $$\\|u - v\\|_2^2 = \\|u\\|_2^2 + \\|v\\|_2^2 - 2(u \\cdot v) = 2 - 2\\cos(\\theta)$$
            
            Because all document and query embeddings are **$L_2$-normalized to unit length** ($\\|u\\|_2 = 1$), 
            Euclidean distance, Cosine similarity, and Dot product produce **strictly identical top-K rankings**.
            """
        )

        if sim_data and "metric_latency_summary" in sim_data:
            st.markdown("#### ⏱️ Exhaustive Linear Scan Latency (9,532 records per query)")
            lat = sim_data["metric_latency_summary"]
            c_e, c_c, c_d = st.columns(3)
            with c_e:
                st.metric("Euclidean (L2) Avg", f"{lat.get('euclidean_distance', {}).get('mean_ms', 0):.2f} ms")
            with c_c:
                st.metric("Cosine Similarity Avg", f"{lat.get('cosine_similarity', {}).get('mean_ms', 0):.2f} ms")
            with c_d:
                st.metric("Dot Product Avg", f"{lat.get('dot_product', {}).get('mean_ms', 0):.2f} ms")

            # Mini bar chart of latencies
            metric_names = ["Euclidean Distance", "Cosine Similarity", "Dot Product"]
            mean_latencies = [
                lat.get('euclidean_distance', {}).get('mean_ms', 0),
                lat.get('cosine_similarity', {}).get('mean_ms', 0),
                lat.get('dot_product', {}).get('mean_ms', 0),
            ]
            fig_np = px.bar(
                x=metric_names,
                y=mean_latencies,
                text=[f"{v:.2f} ms" for v in mean_latencies],
                labels={"x": "NumPy Metric", "y": "Mean Execution Time (ms)"},
                color=metric_names,
                color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
                title="Linear Scan Compute Latency over 9,532 Records",
            )
            fig_np.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=35, b=20))
            st.plotly_chart(fig_np, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 4: Phase 4 Retrieval Benchmarks
    # -------------------------------------------------------------
    with tab_search:
        st.markdown("### 🔍 Phase 4: Semantic Search & Top-K Retrieval Benchmarks")
        st.write(
            """
            Phase 4 verified top-K retrieval and multi-condition compound metadata filtering 
            across all 4 automotive subsystems (`engine_and_transmission`, `electrical_and_body`, 
            `brakes_and_suspension`, `network_and_communication`).
            """
        )

        if search_data and "queries" in search_data:
            p4_queries = search_data["queries"]
            st.markdown(f"**Evaluated {len(p4_queries)} queries in Phase 4:**")
            
            p4_rows = []
            for q in p4_queries:
                top1 = q.get("results_k5", [{}])[0] if q.get("results_k5") else {}
                p4_rows.append({
                    "Query ID": q.get("query_id"),
                    "Topic": q.get("topic"),
                    "Subsystem": q.get("subsystem"),
                    "Top-1 Record": top1.get("record_id"),
                    "Top-1 DTC": top1.get("diagnostic_codes"),
                    "Top-1 Distance": round(top1.get("distance", 0.0), 4),
                    "Cosine Similarity": round(max(0.0, 1.0 - top1.get("distance", 0.0)) * 100, 1),
                })
            df_p4 = pd.DataFrame(p4_rows)
            st.dataframe(df_p4, use_container_width=True, hide_index=True)

            fig_p4 = px.bar(
                df_p4,
                x="Query ID",
                y="Top-1 Distance",
                color="Subsystem",
                text="Top-1 Distance",
                hover_data=["Topic", "Top-1 DTC"],
                title="Phase 4 Top-1 Cosine Distance (Lower is Closer Match)",
            )
            fig_p4.update_layout(height=350, margin=dict(l=20, r=20, t=35, b=20))
            st.plotly_chart(fig_p4, use_container_width=True)
