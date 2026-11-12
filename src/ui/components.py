"""Reusable UI components, resource caching, and enhanced visual styling for Streamlit.

Provides a modern automotive engineering design system, responsive glassmorphism
cards, interactive similarity meters, prominent safety warning banners, and cached
pipeline singletons for high responsiveness.
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
    """Injects modern, clean academic and automotive engineering styling."""
    st.markdown(
        """
        <style>
        /* Base typography & variables */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {
            --primary-navy: #0F172A;
            --accent-blue: #2563EB;
            --accent-indigo: #4F46E5;
            --accent-emerald: #059669;
            --accent-amber: #D97706;
            --accent-rose: #DC2626;
            --card-bg: #FFFFFF;
            --border-light: #E2E8F0;
            --text-dark: #0F172A;
            --text-muted: #64748B;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Hero and Header Elements */
        .hero-banner {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #1E3A8A 100%);
            border-radius: 16px;
            padding: 2.2rem 2.5rem;
            color: #FFFFFF;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25), 0 8px 10px -6px rgba(15, 23, 42, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }
        .hero-banner::after {
            content: "🚗";
            position: absolute;
            right: 2rem;
            bottom: -1rem;
            font-size: 7rem;
            opacity: 0.08;
            pointer-events: none;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(37, 99, 235, 0.35);
            border: 1px solid rgba(96, 165, 250, 0.5);
            color: #93C5FD;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 0.3rem 0.85rem;
            border-radius: 9999px;
            margin-bottom: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin: 0 0 0.5rem 0;
            color: #FFFFFF;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #CBD5E1;
            margin: 0;
            line-height: 1.5;
            max-width: 850px;
        }

        /* Header in page views */
        .main-header {
            font-size: 2.1rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .sub-header {
            font-size: 1.0rem;
            color: #64748B;
            margin-bottom: 1.75rem;
            line-height: 1.5;
        }

        /* Interactive KPI Metric Cards */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 1.75rem;
        }
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
            border-color: #CBD5E1;
        }
        .kpi-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #2563EB, #4F46E5);
        }
        .kpi-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.6rem;
        }
        .kpi-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .kpi-icon {
            font-size: 1.3rem;
            background: #F1F5F9;
            padding: 0.4rem;
            border-radius: 8px;
            line-height: 1;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 0.35rem;
        }
        .kpi-subtext {
            font-size: 0.8rem;
            font-weight: 500;
            color: #059669;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .kpi-subtext.neutral {
            color: #64748B;
        }
        .kpi-subtext.warning {
            color: #D97706;
        }

        /* Diagnostic Knowledge Cards */
        .diag-card {
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
            position: relative;
            border-left: 5px solid #2563EB;
        }
        .diag-card:hover {
            border-color: #93C5FD;
            box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.1);
            transform: translateY(-1px);
        }
        .diag-card.severity-critical { border-left-color: #DC2626; }
        .diag-card.severity-high { border-left-color: #EA580C; }
        .diag-card.severity-medium { border-left-color: #D97706; }
        .diag-card.severity-low { border-left-color: #059669; }

        .diag-card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.45rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .diag-card-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.75rem;
        }
        .metric-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.2rem 0.6rem;
            font-size: 0.78rem;
            font-weight: 600;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .badge-system { background-color: #EFF6FF; color: #1E40AF; border: 1px solid #DBEAFE; }
        .badge-id { background-color: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; font-family: 'JetBrains Mono', monospace; }
        .badge-dtc { background-color: #EEF2FF; color: #4338CA; border: 1px solid #E0E7FF; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
        .badge-severity-critical { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FEE2E2; }
        .badge-severity-high { background-color: #FFF7ED; color: #9A3412; border: 1px solid #FFEDD5; }
        .badge-severity-medium { background-color: #FFFBEB; color: #92400E; border: 1px solid #FEF3C7; }
        .badge-severity-low { background-color: #F0FDF4; color: #166534; border: 1px solid #DCFCE7; }
        
        .diag-similarity-bar {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
            padding: 0.4rem 0.6rem;
            background: #F8FAFC;
            border-radius: 6px;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
        }
        .sim-meter {
            flex-grow: 1;
            height: 6px;
            background: #E2E8F0;
            border-radius: 3px;
            overflow: hidden;
        }
        .sim-meter-fill {
            height: 100%;
            background: linear-gradient(90deg, #3B82F6, #10B981);
            border-radius: 3px;
        }
        .diag-card-excerpt {
            font-size: 0.92rem;
            color: #334155;
            line-height: 1.5;
            background: #FAFAFA;
            padding: 0.65rem 0.85rem;
            border-radius: 6px;
            border: 1px solid #F1F5F9;
        }

        /* Safety Callout Boxes */
        .alert-danger {
            border-left: 5px solid #DC2626;
            background-color: #FEF2F2;
            padding: 1.1rem 1.35rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(220, 38, 38, 0.05);
            border-top: 1px solid #FEE2E2;
            border-right: 1px solid #FEE2E2;
            border-bottom: 1px solid #FEE2E2;
        }
        .alert-critical {
            border-left: 5px solid #EA580C;
            background-color: #FFF7ED;
            padding: 1.1rem 1.35rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(234, 88, 12, 0.05);
            border-top: 1px solid #FFEDD5;
            border-right: 1px solid #FFEDD5;
            border-bottom: 1px solid #FFEDD5;
        }
        .alert-warning {
            border-left: 5px solid #D97706;
            background-color: #FFFBEB;
            padding: 1.1rem 1.35rem;
            border-radius: 0 10px 10px 0;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(217, 119, 6, 0.05);
            border-top: 1px solid #FEF3C7;
            border-right: 1px solid #FEF3C7;
            border-bottom: 1px solid #FEF3C7;
        }
        .alert-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #0F172A;
            margin-bottom: 0.35rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .alert-body {
            font-size: 0.94rem;
            color: #334155;
            line-height: 1.5;
        }
        .alert-action {
            font-size: 0.9rem;
            font-weight: 700;
            color: #0F172A;
            margin-top: 0.6rem;
            padding-top: 0.5rem;
            border-top: 1px dashed rgba(0, 0, 0, 0.1);
        }

        /* Diagnostic Report Output Container */
        .report-container {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 12px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.5rem;
        }
        .report-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #E2E8F0;
        }

        /* Sidebar Styling */
        .sidebar-brand-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.85rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 4px;
        }
        .status-dot.online {
            background-color: #10B981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
            animation: pulse 2s infinite;
        }
        .status-dot.simulated {
            background-color: #F59E0B;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { transform: scale(1); box-shadow: 0 0 0 5px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Feature cards on home */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }
        .feature-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1.1rem;
            transition: all 0.15s ease;
        }
        .feature-card:hover {
            border-color: #3B82F6;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .feature-card-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .feature-card-title {
            font-weight: 700;
            font-size: 0.98rem;
            color: #0F172A;
            margin-bottom: 0.25rem;
        }
        .feature-card-desc {
            font-size: 0.85rem;
            color: #64748B;
            line-height: 1.4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header(title: str, subtitle: str, badge: str = "BITS Pilani WILP Assignment 2") -> None:
    """Renders an executive, modern hero banner."""
    html = f"""
    <div class="hero-banner">
        <div class="hero-badge">🎓 {badge}</div>
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    subtext: str,
    icon: str = "📊",
    status: str = "normal",
) -> None:
    """Renders a custom styled KPI metric card."""
    subtext_class = "neutral"
    if status == "success":
        subtext_class = ""
    elif status == "warning":
        subtext_class = "warning"

    html = f"""
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-label">{label}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext {subtext_class}">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


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
            {f'<div class="alert-action">Mandatory Action: {action}</div>' if action else ''}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_diagnostic_card(doc: Dict[str, Any], rank: int) -> None:
    """Renders an enhanced individual retrieved diagnostic knowledge card."""
    rec_id = doc.get("record_id", "UNKNOWN")
    title = doc.get("title", "Diagnostic Record")
    codes = doc.get("diagnostic_codes", "N/A")
    system = doc.get("vehicle_system", "general").replace("_", " ").title()
    severity = doc.get("severity", "medium").lower()
    dist = doc.get("distance", 0.0)
    sim = doc.get("similarity_score", max(0.0, 1.0 - dist))
    sim_pct = int(min(100, max(0, sim * 100)))
    excerpt = doc.get("excerpt", doc.get("document", ""))[:280]

    sev_badge_class = f"badge-severity-{severity}"
    sev_card_class = f"severity-{severity}"

    st.markdown(
        f"""
        <div class="diag-card {sev_card_class}">
            <div class="diag-card-title">
                <span>#{rank} — {title}</span>
                <span class="metric-badge badge-dtc">DTC: {codes}</span>
            </div>
            <div class="diag-card-meta">
                <span class="metric-badge badge-system">📁 {system}</span>
                <span class="metric-badge {sev_badge_class}">⚡ {severity.upper()}</span>
                <span class="metric-badge badge-id">ID: {rec_id}</span>
            </div>
            <div class="diag-card-excerpt">
                {excerpt}...
            </div>
            <div class="diag-similarity-bar">
                <span>Similarity Match: <strong>{sim_pct}%</strong> (Cosine Dist: <code>{dist:.4f}</code>)</span>
                <div class="sim-meter">
                    <div class="sim-meter-fill" style="width: {sim_pct}%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status() -> None:
    """Renders active system telemetry and environment status in the sidebar."""
    chroma_mgr = get_cached_chroma_manager()
    count = chroma_mgr.get_count()

    rag = get_cached_rag_pipeline()
    provider = rag.llm_provider
    gen_mode = getattr(provider, "generation_mode", "unknown")

    if gen_mode == "real":
        status_html = '<span class="status-dot online"></span><strong style="color:#059669;">Ollama Live</strong>'
        model_sub = f"<code>{provider.name}</code> ({provider.model_name})"
    else:
        status_html = '<span class="status-dot simulated"></span><strong style="color:#D97706;">Mock Simulation</strong>'
        model_sub = "<code>MockLLMProvider</code> (Deterministic)"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand-box">
            <div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; letter-spacing:0.05em; font-weight:700; margin-bottom:0.4rem;">
                System Telemetry
            </div>
            <div style="font-size:0.88rem; margin-bottom:0.35rem;">
                <strong>Vector Store:</strong> <code>{CHROMA_COLLECTION_NAME}</code>
            </div>
            <div style="font-size:0.88rem; margin-bottom:0.35rem;">
                <strong>Indexed DTCs:</strong> <span style="font-weight:700; color:#2563EB;">{count:,}</span> records
            </div>
            <div style="font-size:0.88rem; margin-bottom:0.35rem;">
                <strong>Embeddings:</strong> <code>all-MiniLM-L6-v2</code> (384d)
            </div>
            <div style="font-size:0.88rem; margin-top:0.4rem; padding-top:0.4rem; border-top:1px dashed #E2E8F0;">
                <strong>Inference:</strong> {status_html}<br/>
                <span style="font-size:0.8rem; color:#64748B;">{model_sub}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
