"""Reusable UI components, resource caching, and visual styling for Streamlit.

Provides unified styling, diagnostic knowledge cards, safety warning banners,
metric tiles, and cached pipeline initialization for responsiveness.
"""

from typing import Any, Dict, List, Optional
import streamlit as st

from src.chroma_manager import ChromaDBManager
from src.config import CHROMA_COLLECTION_NAME, DEFAULT_EMBEDDING_MODEL
from src.llm_provider import get_llm_provider
from src.rag_pipeline import RAGPipeline
from src.semantic_search import SemanticSearchEngine


@st.cache_resource(show_spinner=False)
def get_cached_chroma_manager() -> ChromaDBManager:
    """Returns a cached singleton ChromaDBManager instance."""
    return ChromaDBManager()


@st.cache_resource(show_spinner=False)
def get_cached_search_engine() -> SemanticSearchEngine:
    """Returns a cached singleton SemanticSearchEngine instance."""
    manager = get_cached_chroma_manager()
    return SemanticSearchEngine(chroma_manager=manager)


@st.cache_resource(show_spinner=False)
def get_cached_rag_pipeline(provider_name: Optional[str] = None) -> RAGPipeline:
    """Returns a cached singleton RAGPipeline instance."""
    manager = get_cached_chroma_manager()
    search_engine = get_cached_search_engine()
    provider = get_llm_provider(provider_name=provider_name, allow_mock_fallback=True)
    return RAGPipeline(
        search_engine=search_engine,
        llm_provider=provider,
        chroma_manager=manager,
        default_top_k=5,
    )


def inject_custom_css() -> None:
    """Injects modern, clean academic styling with responsive layout and clear hierarchy."""
    st.markdown(
        """
        <style>
        /* Base typography & spacing */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .metric-badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 9999px;
            margin-right: 0.4rem;
        }
        .badge-system { background-color: #E0E7FF; color: #3730A3; }
        .badge-severity-critical { background-color: #FEE2E2; color: #991B1B; }
        .badge-severity-high { background-color: #FFEDD5; color: #9A3412; }
        .badge-severity-medium { background-color: #FEF3C7; color: #92400E; }
        .badge-severity-low { background-color: #DCFCE7; color: #166534; }
        
        /* Diagnostic card styling */
        .diag-card {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.85rem;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: border-color 0.15s ease-in-out;
        }
        .diag-card:hover {
            border-color: #3B82F6;
        }
        .diag-card-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 0.35rem;
        }
        .diag-card-meta {
            font-size: 0.85rem;
            color: #6B7280;
            margin-bottom: 0.5rem;
        }
        .diag-card-excerpt {
            font-size: 0.92rem;
            color: #374151;
            line-height: 1.45;
        }

        /* Safety callout boxes */
        .alert-danger {
            border-left: 5px solid #DC2626;
            background-color: #FEF2F2;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
        }
        .alert-critical {
            border-left: 5px solid #EA580C;
            background-color: #FFF7ED;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
        }
        .alert-warning {
            border-left: 5px solid #D97706;
            background-color: #FFFBEB;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
        }
        .alert-title {
            font-weight: 700;
            font-size: 1.0rem;
            margin-bottom: 0.25rem;
        }
        .alert-body {
            font-size: 0.92rem;
            line-height: 1.4;
        }
        .alert-action {
            font-size: 0.88rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        /* Sidebar info block */
        .sidebar-section {
            padding: 0.75rem 0.5rem;
            border-radius: 6px;
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            margin-bottom: 1rem;
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_safety_alerts(alerts: List[Dict[str, Any]]) -> None:
    """Renders prominent, color-coded automotive safety alerts."""
    if not alerts:
        return

    for alert in alerts:
        severity = alert.get("severity", "WARNING").upper()
        title = alert.get("title", "Safety Warning")
        message = alert.get("message", "")
        action = alert.get("recommended_action", "")

        css_class = "alert-warning"
        icon = "⚠️"
        if severity == "DANGER":
            css_class = "alert-danger"
            icon = "🛑"
        elif severity == "CRITICAL":
            css_class = "alert-critical"
            icon = "🚨"

        html = f"""
        <div class="{css_class}">
            <div class="alert-title">{icon} {title}</div>
            <div class="alert-body">{message}</div>
            {f'<div class="alert-action">Recommended Action: {action}</div>' if action else ''}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_diagnostic_card(doc: Dict[str, Any], rank: int) -> None:
    """Renders an individual retrieved diagnostic knowledge card with distance & metadata."""
    rec_id = doc.get("record_id", "UNKNOWN")
    title = doc.get("title", "Diagnostic Record")
    codes = doc.get("diagnostic_codes", "N/A")
    system = doc.get("vehicle_system", "general").replace("_", " ").title()
    severity = doc.get("severity", "medium").lower()
    dist = doc.get("distance", 0.0)
    sim = doc.get("similarity_score", 1.0 - dist)
    excerpt = doc.get("excerpt", doc.get("document", ""))[:280]

    sev_badge_class = f"badge-severity-{severity}"

    st.markdown(
        f"""
        <div class="diag-card">
            <div class="diag-card-title">#{rank} — {title}</div>
            <div class="diag-card-meta">
                <span class="metric-badge badge-system">📁 {system}</span>
                <span class="metric-badge {sev_badge_class}">⚡ Severity: {severity.upper()}</span>
                <span style="font-family: monospace; font-weight: 600; margin-left: 0.5rem; color: #1E40AF;">
                    ID: {rec_id} | DTC: {codes}
                </span>
                <span style="float: right; font-family: monospace; color: #4B5563;">
                    Cosine Distance: <strong>{dist:.4f}</strong> (Sim: <strong>{sim:.4f}</strong>)
                </span>
            </div>
            <div class="diag-card-excerpt">
                {excerpt}...
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status() -> None:
    """Renders active system telemetry and environment status in the sidebar."""
    chroma_mgr = get_cached_chroma_manager()
    count = chroma_mgr.get_count()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Backend System Status")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Vector Records", f"{count:,}")
    with col2:
        st.metric("Embed Dims", "384")

    # Inspect active LLM provider dynamically
    rag = get_cached_rag_pipeline()
    provider = rag.llm_provider
    gen_mode = getattr(provider, "generation_mode", "unknown")
    if gen_mode == "real":
        provider_badge = f"<span style='color:#16A34A; font-weight:600;'>● Live ({provider.name})</span><br/><code>{provider.model_name}</code>"
    else:
        provider_badge = f"<span style='color:#DC2626; font-weight:600;'>⚠️ Simulated Fallback</span><br/><code>Ollama Daemon Offline</code>"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-section">
            <strong>ChromaDB Collection:</strong><br/>
            <code>{CHROMA_COLLECTION_NAME}</code><br/>
            <strong>Embedding Model:</strong><br/>
            <code>all-MiniLM-L6-v2</code><br/>
            <strong>LLM Provider Status:</strong><br/>
            {provider_badge}
        </div>
        """,
        unsafe_allow_html=True,
    )
