#!/usr/bin/env python3
"""Executes semantic search and metadata-filtered retrieval experiments against ChromaDB.

Runs the 10 assignment queries for K=5 and K=10, executes 5 multi-condition metadata
filter experiments, performs validation checks, and saves structured JSON and
human-readable Markdown reports.

Usage:
    python scripts/run_queries.py
"""

from pathlib import Path
import sys
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.chroma_manager import ChromaDBManager
from src.config import EXPERIMENTS_DIR, QUERIES_FILE
from src.metadata_filters import ASSIGNMENT_FILTER_PRESETS
from src.semantic_search import SemanticSearchEngine
from src.utils import load_json, save_json, setup_logger

logger = setup_logger("run_queries")


def run_topk_experiments(search_engine: SemanticSearchEngine, queries: list) -> dict:
    """Executes top-5 and top-10 retrieval for all 10 assignment queries."""
    logger.info("Executing Top-K retrieval benchmarks for all 10 queries...")
    results_payload = {
        "metadata": {
            "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_queries": len(queries),
            "collection_name": search_engine.chroma_manager.collection_name,
            "total_collection_records": search_engine.chroma_manager.get_count(),
            "embedding_model": search_engine.embedding_manager.model_name,
            "distance_metric": search_engine.chroma_manager.distance_metric,
        },
        "queries": [],
    }

    for q in queries:
        qid = q["query_id"]
        qtext = q["query_text"]
        logger.info(f"Running Query {qid} (K=5 and K=10)...")

        # Top-5 Retrieval
        top5 = search_engine.search(query=qtext, top_k=5, query_id=qid)

        # Top-10 Retrieval
        top10 = search_engine.search(query=qtext, top_k=10, query_id=qid)

        # Verification: order by distance ascending
        for r_list, k_val in [(top5, 5), (top10, 10)]:
            dists = [r["distance"] for r in r_list]
            if dists != sorted(dists):
                raise ValueError(f"Results for {qid} (K={k_val}) are not ordered ascending by distance: {dists}")
            ids = [r["id"] for r in r_list]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate IDs found in results for {qid} (K={k_val}): {ids}")

        results_payload["queries"].append({
            "query_id": qid,
            "query_text": qtext,
            "topic": q.get("topic", ""),
            "subsystem": q.get("subsystem", ""),
            "brief_rationale": q.get("brief_rationale", ""),
            "top_5": top5,
            "top_10": top10,
        })

    return results_payload


def run_metadata_filter_experiments(search_engine: SemanticSearchEngine) -> dict:
    """Executes 5 multi-condition metadata-filtered search experiments."""
    logger.info("Executing 5 Multi-Condition Metadata Filter Experiments...")
    filter_results = {
        "metadata": {
            "execution_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_filter_experiments": len(ASSIGNMENT_FILTER_PRESETS),
            "collection_name": search_engine.chroma_manager.collection_name,
        },
        "experiments": [],
    }

    for preset in ASSIGNMENT_FILTER_PRESETS:
        fid = preset["filter_id"]
        fname = preset["name"]
        qtext = preset["query_text"]
        fcond = preset["filter"]

        logger.info(f"Running Filter Experiment {fid}: {fname}...")
        results = search_engine.search(
            query=qtext,
            top_k=5,
            query_id=fid,
            where=fcond,
        )

        # Verify that all returned records strictly satisfy the filter conditions
        for r in results:
            meta = r["metadata"]
            # Check $and conditions
            if "$and" in fcond:
                for cond in fcond["$and"]:
                    for field, op_dict in cond.items():
                        expected = op_dict["$eq"]
                        actual = meta.get(field)
                        if actual != expected:
                            raise ValueError(
                                f"Record {r['id']} failed filter on '{field}'. Expected '{expected}', got '{actual}'"
                            )

        filter_results["experiments"].append({
            "filter_id": fid,
            "name": fname,
            "description": preset["description"],
            "query_text": qtext,
            "filter_conditions": fcond,
            "results_count": len(results),
            "results": results,
        })

    return filter_results


def generate_semantic_search_markdown(data: dict, out_file: Path):
    """Generates a clean Markdown report for the top-K query results."""
    lines = [
        "# Semantic Search & Top-K Retrieval Experiment Results",
        "",
        f"**Collection:** `{data['metadata']['collection_name']}`  ",
        f"**Total Indexed Documents:** {data['metadata']['total_collection_records']:,}  ",
        f"**Embedding Model:** `{data['metadata']['embedding_model']}` (384 dimensions)  ",
        f"**Distance Metric:** `{data['metadata']['distance_metric']}` (Cosine distance: 0.0 = identical, 1.0 = orthogonal)  ",
        f"**Execution Timestamp:** {data['metadata']['execution_timestamp']}  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "Each of the 10 diverse automotive troubleshooting queries was executed against the persistent ChromaDB database for both **K=5** and **K=10**. All result lists are strictly ranked by cosine distance (ascending). Zero ID collisions were detected in any query result list.",
        "",
        "---",
        "",
    ]

    for q in data["queries"]:
        qid = q["query_id"]
        lines.append(f"### Query {qid}: {q['topic']}")
        lines.append(f"**Query Text:** *\"{q['query_text']}\"*  ")
        lines.append(f"**Subsystem:** `{q['subsystem']}`  ")
        lines.append(f"**Diagnostic Rationale:** {q['brief_rationale']}  ")
        lines.append("")
        lines.append("#### Top-5 Retrieved Records:")
        lines.append("")
        lines.append("| Rank | Record ID | Title | Distance | Cosine Similarity | Severity | System |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in q["top_5"]:
            lines.append(
                f"| {r['rank']} | `{r['id']}` | {r['title'][:45]} | {r['distance']:.4f} | {r['similarity_score']:.4f} | `{r['severity']}` | `{r['vehicle_system']}` |"
            )
        lines.append("")
        lines.append("**Top Match Excerpt:**")
        top_rec = q["top_5"][0]
        lines.append(f"> **{top_rec['title']}** (`{top_rec['id']}`):  ")
        lines.append(f"> {top_rec['excerpt']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Saved readable report to {out_file}")


def generate_metadata_filter_markdown(data: dict, out_file: Path):
    """Generates a clean Markdown report for the metadata filter experiments."""
    lines = [
        "# Multi-Condition Metadata Filtering Experiment Results",
        "",
        f"**Collection:** `{data['metadata']['collection_name']}`  ",
        f"**Experiments Executed:** {data['metadata']['total_filter_experiments']} multi-condition filters  ",
        f"**Execution Timestamp:** {data['metadata']['execution_timestamp']}  ",
        "",
        "---",
        "",
        "## Filter Design & Verification Overview",
        "",
        "ChromaDB enforces metadata filtering using structured boolean operator objects (`$and`, `$or`). Each experiment below verifies that compound filter constraints are strictly obeyed, preventing domain cross-talk and restricting search space to authenticated subsystem partitions.",
        "",
        "---",
        "",
    ]

    for exp in data["experiments"]:
        fid = exp["filter_id"]
        lines.append(f"### Experiment {fid}: {exp['name']}")
        lines.append(f"**Description:** {exp['description']}  ")
        lines.append(f"**Query Text:** *\"{exp['query_text']}\"*  ")
        lines.append(f"**Filter Expression:** `{exp['filter_conditions']}`  ")
        lines.append(f"**Results Found:** {exp['results_count']} records  ")
        lines.append("")
        lines.append("| Rank | Record ID | Title | Distance | Severity | Vehicle System |")
        lines.append("|---|---|---|---|---|---|")
        for r in exp["results"]:
            lines.append(
                f"| {r['rank']} | `{r['id']}` | {r['title'][:45]} | {r['distance']:.4f} | `{r['severity']}` | `{r['vehicle_system']}` |"
            )
        lines.append("")
        lines.append("**Compliance Check:** All returned records verified matching filter criteria.")
        lines.append("")
        lines.append("---")
        lines.append("")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Saved readable filter report to {out_file}")


def main():
    logger.info("Starting Phase 4 query and filter execution script...")

    # Load queries
    if not QUERIES_FILE.exists():
        logger.error(f"Queries file not found at {QUERIES_FILE}")
        sys.exit(1)
    queries = load_json(QUERIES_FILE)
    logger.info(f"Loaded {len(queries)} assignment queries from {QUERIES_FILE}")

    # Initialize ChromaDB and Search Engine
    chroma_mgr = ChromaDBManager()
    search_engine = SemanticSearchEngine(chroma_manager=chroma_mgr)

    initial_count = chroma_mgr.get_count()
    if initial_count != 9532:
        logger.error(f"Expected 9,532 records in collection, found {initial_count}!")
        sys.exit(1)

    # 1. Run Top-K retrieval experiments
    semantic_results = run_topk_experiments(search_engine, queries)
    json_path = EXPERIMENTS_DIR / "semantic_search_results.json"
    md_path = EXPERIMENTS_DIR / "semantic_search_results.md"
    save_json(semantic_results, json_path)
    generate_semantic_search_markdown(semantic_results, md_path)

    # 2. Run Metadata Filter experiments
    filter_results = run_metadata_filter_experiments(search_engine)
    filter_json_path = EXPERIMENTS_DIR / "metadata_filter_results.json"
    filter_md_path = EXPERIMENTS_DIR / "metadata_filter_results.md"
    save_json(filter_results, filter_json_path)
    generate_metadata_filter_markdown(filter_results, filter_md_path)

    # 3. Post-execution collection integrity check
    post_count = chroma_mgr.get_count()
    if post_count != initial_count:
        logger.error(f"Collection count changed after search experiments: {initial_count} -> {post_count}")
        sys.exit(1)
    logger.info(f"Integrity check PASSED: Collection count remains {post_count}.")

    print("\n" + "=" * 60)
    print("PHASE 4 EXPERIMENTS EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Assignment Queries Executed:   {len(queries)}")
    print(f"Top-K Benchmark Configurations:      K=5 and K=10 for all 10 queries")
    print(f"Multi-Condition Metadata Filters:    5 distinct compound filters verified")
    print(f"Semantic Search Output (JSON):       {json_path}")
    print(f"Semantic Search Output (Markdown):   {md_path}")
    print(f"Metadata Filter Output (JSON):       {filter_json_path}")
    print(f"Metadata Filter Output (Markdown):   {filter_md_path}")
    print(f"ChromaDB Collection Intact:          {post_count} records (Unchanged)")
    print("Status:                              SUCCESS & VERIFIED")


if __name__ == "__main__":
    main()
