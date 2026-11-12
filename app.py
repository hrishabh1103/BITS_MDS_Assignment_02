"""Vehicle Troubleshooting Assistant — Streamlit Multi-Page Web Application.

BITS Pilani WILP — Modern Database Systems (Assignment 2)
Academic Project: Persistent ChromaDB & Grounded Retrieval-Augmented Generation (RAG).
Group: Group 20 | Verified Commit: a073712 / 20403a2
"""

import streamlit as st

from src.ui.about_page import render_about_page
from src.ui.assistant_page import render_assistant_page
from src.ui.components import inject_custom_css, render_sidebar_status
from src.ui.evaluation_page import render_evaluation_page
from src.ui.home_page import render_home_page
from src.ui.search_page import render_search_page


def main() -> None:
    """Main application orchestrator and multi-page routing hub."""
    st.set_page_config(
        page_title="AutoTroubleshoot AI — Vehicle Troubleshooting Assistant",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject modern visual styles and design system
    inject_custom_css()

    # Sidebar Header & Branding
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
            <span style="font-size:2.2rem;">🚗</span>
            <div>
                <div style="font-size:1.15rem; font-weight:800; color:#0F172A; line-height:1.2;">AutoTroubleshoot AI</div>
                <div style="font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Group 20 • WILP MDS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div style="font-size:0.8rem; color:#475569; background:#F8FAFC; border:1px solid #E2E8F0; padding:0.5rem 0.65rem; border-radius:8px; margin-bottom:1rem; line-height:1.4;">
            <strong>Course:</strong> Modern Database Systems<br/>
            <strong>Assignment:</strong> 2 (Persistent Vector DB & RAG)
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_selection = st.sidebar.radio(
        "Navigation Menu:",
        options=[
            "🏠 Home / Dashboard",
            "🔧 Troubleshooting Assistant",
            "🔍 Semantic Search",
            "📊 Evaluation Dashboard",
            "📖 About / Dataset",
        ],
        index=0,
    )

    # Render Active System Telemetry
    render_sidebar_status()

    # Quick Navigation Help in Sidebar
    st.sidebar.markdown(
        """
        <div style="font-size:0.78rem; color:#94A3B8; text-align:center; padding-top:0.75rem; border-top:1px solid #E2E8F0;">
            BITS Pilani WILP © 2026<br/>
            Persistent Vector Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Route to Selected View
    if nav_selection == "🏠 Home / Dashboard":
        render_home_page()
    elif nav_selection == "🔧 Troubleshooting Assistant":
        render_assistant_page()
    elif nav_selection == "🔍 Semantic Search":
        render_search_page()
    elif nav_selection == "📊 Evaluation Dashboard":
        render_evaluation_page()
    elif nav_selection == "📖 About / Dataset":
        render_about_page()

    # Academic Footer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; color: #94A3B8; font-size: 0.82rem; padding: 1.5rem 0; border-top: 1px solid #E2E8F0;">
            <strong>BITS Pilani WILP — Modern Database Systems (Assignment 2)</strong> | Official Group: <strong>Group 20</strong><br/>
            Knowledge Base: <code>vehicle_troubleshooting_kb</code> (9,532 Persistent Vectors) | Model: <code>all-MiniLM-L6-v2</code> (384-dim, $L_2$ Normalized)
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
