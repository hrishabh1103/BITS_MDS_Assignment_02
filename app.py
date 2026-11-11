"""Vehicle Troubleshooting Assistant — Streamlit Multi-Page Web Application.

BITS Pilani WILP — Modern Database Systems (Assignment 2)
Academic Project: Persistent ChromaDB & Grounded Retrieval-Augmented Generation (RAG).
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
        page_title="Vehicle Troubleshooting Assistant",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject modern visual styles
    inject_custom_css()

    # Sidebar Header & Navigation
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/BITS_Pilani-Logo.svg/300px-BITS_Pilani-Logo.svg.png",
        width=70,
    )
    st.sidebar.markdown("## 🚗 AutoTroubleshoot AI")
    st.sidebar.markdown(
        "<div style='font-size:0.85rem; color:#6B7280; margin-bottom:1rem;'>"
        "BITS Pilani WILP | Modern Database Systems<br/>Assignment 2: ChromaDB & RAG"
        "</div>",
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
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #9CA3AF; font-size: 0.85rem; padding: 1rem 0;'>"
        "BITS Pilani WILP — Modern Database Systems (Assignment 2) | Vehicle Troubleshooting Assistant<br/>"
        "Knowledge Base: 9,532 Persistent ChromaDB Records (Cosine Space) | Embeddings: all-MiniLM-L6-v2 (384-dim)"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
