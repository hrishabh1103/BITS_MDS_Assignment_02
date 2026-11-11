"""Generates a professional academic system architecture diagram for Phase 8 submission.

Diagram shows:
Dataset -> Preprocessing -> Sentence Transformer -> ChromaDB -> Semantic Retrieval -> Context Construction -> LLM -> Grounded Answer with Citations -> Streamlit UI
With NumPy evaluation as a separate experimental path.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path


def create_architecture_diagram(output_path: str = "reports/figures/system_architecture.png") -> None:
    fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Title
    ax.text(
        7.0, 8.6,
        "Vehicle Troubleshooting Assistant — End-to-End System Architecture",
        fontsize=16, fontweight="bold", ha="center", va="center", color="#1E3A8A"
    )
    ax.text(
        7.0, 8.25,
        "BITS Pilani WILP — Modern Database Systems (Assignment 2) | ChromaDB & Grounded RAG Pipeline",
        fontsize=10, ha="center", va="center", color="#4B5563"
    )

    # Styles
    box_blue = dict(boxstyle="round,pad=0.5", fc="#EFF6FF", ec="#3B82F6", lw=1.5)
    box_indigo = dict(boxstyle="round,pad=0.5", fc="#EEF2FF", ec="#6366F1", lw=1.5)
    box_green = dict(boxstyle="round,pad=0.5", fc="#F0FDF4", ec="#22C55E", lw=1.5)
    box_amber = dict(boxstyle="round,pad=0.5", fc="#FFFBEB", ec="#F59E0B", lw=1.5)
    box_red = dict(boxstyle="round,pad=0.5", fc="#FEF2F2", ec="#EF4444", lw=1.5)
    box_purple = dict(boxstyle="round,pad=0.5", fc="#FAF5FF", ec="#A855F7", lw=1.5)

    arrow_props = dict(arrowstyle="->", lw=1.8, color="#1E293B", shrinkA=5, shrinkB=5)
    dash_arrow = dict(arrowstyle="->", lw=1.8, color="#DC2626", ls="--", shrinkA=5, shrinkB=5)

    # 1. Dataset Box
    ax.text(
        2.0, 7.0,
        "1. Raw Automotive Data\n• Zenodo (Rec 15626055)\n• OBDex KB (CC0 1.0)\n• 9,533 Ingested Records",
        fontsize=9, ha="center", va="center", bbox=box_blue
    )

    # 2. Preprocessing & Validation
    ax.text(
        5.2, 7.0,
        "2. Preprocessing & Schema\n• Text sanitization & dedup\n• Schema validation engine\n• 9,532 Unique Valid Records",
        fontsize=9, ha="center", va="center", bbox=box_blue
    )

    # 3. Embedding Model
    ax.text(
        8.8, 7.0,
        "3. Sentence-Transformer\n• all-MiniLM-L6-v2\n• 384 Dense Float32 Dims\n• Unit-normalized vectors",
        fontsize=9, ha="center", va="center", bbox=box_indigo
    )

    # 4. ChromaDB Storage
    ax.text(
        12.0, 7.0,
        "4. Persistent ChromaDB\n• vehicle_troubleshooting_kb\n• Space: Cosine (HNSW Index)\n• 9,532 Records (~180MB)",
        fontsize=9, ha="center", va="center", bbox=box_green
    )

    # Horizontal Arrows for Pipeline Prep
    ax.annotate("", xy=(3.8, 7.0), xytext=(3.2, 7.0), arrowprops=arrow_props)
    ax.annotate("", xy=(7.4, 7.0), xytext=(6.8, 7.0), arrowprops=arrow_props)
    ax.annotate("", xy=(10.5, 7.0), xytext=(10.0, 7.0), arrowprops=arrow_props)

    # Downward branching: Semantic Search & NumPy Comparison
    ax.annotate("", xy=(12.0, 5.5), xytext=(12.0, 6.2), arrowprops=arrow_props)

    # 5. Semantic Vector Retrieval & Filtering
    ax.text(
        12.0, 4.8,
        "5. Semantic Search Engine\n• Top-K Retrieval (Cosine)\n• Metadata Filters ($and)\n• Queries Q01–Q10",
        fontsize=9, ha="center", va="center", bbox=box_green
    )

    # Branch to NumPy (Left from step 4/5)
    ax.annotate("", xy=(8.5, 4.8), xytext=(10.2, 4.8), arrowprops=dash_arrow)

    # NumPy Exhaustive Comparison Path
    ax.text(
        6.5, 4.8,
        "Exhaustive NumPy Engine\n(Independent Validation Path)\n• Euclidean Distance (L2)\n• Cosine Similarity\n• Dot Product ($K=5, 10$)\n• Linear Scan across 9,532",
        fontsize=8.5, ha="center", va="center", bbox=box_red
    )

    # Down from 5 to 6: Context Construction & Guardrails
    ax.annotate("", xy=(12.0, 3.2), xytext=(12.0, 4.0), arrowprops=arrow_props)

    # 6. Context Construction & Automotive Guardrails
    ax.text(
        12.0, 2.5,
        "6. Context & Safety Engine\n• Grounded Prompt Assembly\n• SRS Airbag Prohibitions\n• EV High-Voltage Isolation\n• 12V ICE Domain Mismatch\n• Hydraulic Brake Warning\n• Cooling Scald Precautions",
        fontsize=8.5, ha="center", va="center", bbox=box_amber
    )

    # Left to 7: LLM Generation
    ax.annotate("", xy=(8.8, 2.5), xytext=(10.0, 2.5), arrowprops=arrow_props)

    # 7. LLM Provider (Ollama / Llama 3.2)
    ax.text(
        7.2, 2.5,
        "7. LLM Provider Layer\n• Real: Ollama (Llama 3.2 3B)\n• Grounded Anti-Hallucination\n• Mandatory Citations [VTR-XX]\n• Fallback: MockLLMProvider",
        fontsize=8.5, ha="center", va="center", bbox=box_purple
    )

    # Left to 8: Grounded Answer & Citation Fidelity
    ax.annotate("", xy=(4.5, 2.5), xytext=(5.6, 2.5), arrowprops=arrow_props)

    # 8. Evaluation & Grounded Output
    ax.text(
        3.0, 2.5,
        "8. Diagnostic Synthesis\n• Structured 5-Part Diagnosis\n• Citation Provenance Audit\n  (100% Precision, 96% Recall)\n• Context vs Baseline Audit",
        fontsize=8.5, ha="center", va="center", bbox=box_purple
    )

    # Down to 9: Streamlit UI
    ax.annotate("", xy=(3.0, 1.2), xytext=(3.0, 1.7), arrowprops=arrow_props)

    # 9. Streamlit Dashboard
    ax.text(
        7.0, 0.8,
        "9. Multi-Page Streamlit Web Application (app.py)\n"
        "Page 1: Home / Dashboard  |  Page 2: Troubleshooting Assistant  |  Page 3: Semantic Search\n"
        "Page 4: Empirical Evaluation Dashboard  |  Page 5: Dataset Provenance & Known Limitations",
        fontsize=9, ha="center", va="center", bbox=box_blue
    )
    ax.annotate("", xy=(5.0, 1.1), xytext=(3.8, 1.8), arrowprops=arrow_props)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Architecture diagram generated successfully at: {output_path}")


if __name__ == "__main__":
    create_architecture_diagram()
