"""Script to perform deep verification and reconciliation between Phase 4 and Phase 5.

Verifies:
1. Exact query text identity across queries.json, Phase 4 results, and Phase 5 results.
2. Exact document text, dimension, L2-norm, and SHA-256 vector fingerprints for representative records.
3. Mathematical equivalence between Euclidean, Cosine, and Dot Product on actual vectors.
4. Investigation of reported discrepancies between Phase 4 documentation and Phase 5 results.
5. Exhaustive coverage across all 9,532 records.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

from src.chroma_manager import ChromaDBManager
from src.config import EXPERIMENTS_DIR, BASE_DIR
from src.embeddings import create_record_text
from src.similarity_metrics import euclidean_distance, cosine_similarity, dot_product


def compute_vector_fingerprint(vec: np.ndarray) -> str:
    """Computes a deterministic SHA-256 hex digest of a float32 vector."""
    arr = np.ascontiguousarray(vec, dtype=np.float32)
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


def main():
    print("=" * 80)
    print("PHASE 4 vs PHASE 5 DEEP VERIFICATION AND RECONCILIATION")
    print("=" * 80)

    # 1. Load Query definitions
    with open(BASE_DIR / "data" / "queries" / "assignment_queries.json") as f:
        queries_def = json.load(f)

    # 2. Load Phase 4 results
    with open(EXPERIMENTS_DIR / "semantic_search_results.json") as f:
        phase4_json = json.load(f)

    # 3. Load Phase 5 results
    with open(EXPERIMENTS_DIR / "similarity_comparison_results.json") as f:
        phase5_json = json.load(f)

    # 4. Load dataset
    with open(BASE_DIR / "data" / "processed" / "vehicle_troubleshooting.json") as f:
        dataset = json.load(f)
    dataset_by_id = {r["id"]: r for r in dataset}

    print(f"\n[STEP 2: Query Text Verification]")
    query_text_mismatches = []
    for i, q in enumerate(queries_def):
        qid = q["query_id"]
        text_def = q["query_text"]
        p4_q = phase4_json["queries"][i]
        p5_q = phase5_json["query_evaluations"][i]

        assert p4_q["query_id"] == qid
        assert p5_q["query_id"] == qid

        text_p4 = p4_q["query_text"]
        text_p5 = p5_q["query_text"]

        match_def_p4 = (text_def == text_p4)
        match_def_p5 = (text_def == text_p5)
        match_p4_p5 = (text_p4 == text_p5)

        print(f"  {qid}: def==p4: {match_def_p4} | def==p5: {match_def_p5} | p4==p5: {match_p4_p5}")
        if not (match_def_p4 and match_def_p5 and match_p4_p5):
            query_text_mismatches.append(qid)

    print(f"  Total query text mismatches: {len(query_text_mismatches)}")

    # 5. Connect to ChromaDB and get all vectors
    print(f"\n[STEP 3: Document Embeddings & Fingerprints Verification]")
    chroma_mgr = ChromaDBManager()
    all_chroma = chroma_mgr.collection.get(include=["embeddings", "metadatas", "documents"])
    chroma_ids = all_chroma["ids"]
    chroma_embs = np.array(all_chroma["embeddings"], dtype=np.float32)
    chroma_docs = all_chroma["documents"]
    id_to_idx = {cid: idx for idx, cid in enumerate(chroma_ids)}

    print(f"  Total ChromaDB documents retrieved: {len(chroma_ids)}")
    print(f"  ChromaDB embeddings matrix shape: {chroma_embs.shape}")

    # Test representative records
    target_ids = [
        "VTR-P00B7", "VTR-P0316", "VTR-P2534", "VTR-P0D17",
        "VTR-C0619", "VTR-C0291", "VTR-P0732", "VTR-P2711",
        "VTR-P0300", "VTR-B0860", "VTR-U0039", "VTR-B0223",
        "VTR-P20CF", "VTR-P2BD2", "VTR-B0001", "VTR-B0005", "VTR-P0299"
    ]

    print("\n  Representative Record Embeddings:")
    for rid in target_ids:
        if rid not in id_to_idx:
            print(f"    {rid}: NOT FOUND IN CHROMADB")
            continue
        idx = id_to_idx[rid]
        vec = chroma_embs[idx]
        norm = float(np.linalg.norm(vec))
        fp = compute_vector_fingerprint(vec)
        first5 = [round(float(x), 5) for x in vec[:5]]

        # Compare document text in Chroma with fresh create_record_text from dataset
        raw_rec = dataset_by_id[rid]
        fresh_text = create_record_text(raw_rec)
        stored_text = chroma_docs[idx]
        text_match = (fresh_text.strip() == stored_text.strip())

        print(f"    {rid}: dim={len(vec)} | norm={norm:.6f} | fp={fp} | text_match={text_match} | first5={first5}")

    # 6. Step 4: Mathematical Equivalence on Actual Vectors
    print(f"\n[STEP 4: Mathematical Equivalence on All 10 Queries]")
    for i, q in enumerate(queries_def):
        qid = q["query_id"]
        qtext = q["query_text"]
        q_emb = chroma_mgr.embedding_manager.embed_query(qtext, normalize=True)
        q_norm = float(np.linalg.norm(q_emb))

        euc = euclidean_distance(chroma_embs, q_emb)
        cos = cosine_similarity(chroma_embs, q_emb)
        dot = dot_product(chroma_embs, q_emb)

        # Check max discrepancies
        diff_cos_dot = np.max(np.abs(cos - dot))
        # Theoretical relationship: euc_sq = 2*(1 - cos) => euc = sqrt(2*(1 - cos))
        expected_euc = np.sqrt(np.maximum(0.0, 2.0 * (1.0 - cos)))
        diff_euc_formula = np.max(np.abs(euc - expected_euc))

        # Check top-1, top-5, top-10 IDs
        top10_cos_idx = np.argsort(-cos)[:10]
        top10_dot_idx = np.argsort(-dot)[:10]
        top10_euc_idx = np.argsort(euc)[:10]

        top10_cos_ids = [chroma_ids[j] for j in top10_cos_idx]
        top10_dot_ids = [chroma_ids[j] for j in top10_dot_idx]
        top10_euc_ids = [chroma_ids[j] for j in top10_euc_idx]

        top1_match = (top10_cos_ids[0] == top10_dot_ids[0] == top10_euc_ids[0])
        top5_match = (top10_cos_ids[:5] == top10_dot_ids[:5] == top10_euc_ids[:5])
        top10_match = (top10_cos_ids == top10_dot_ids == top10_euc_ids)

        print(
            f"  {qid}: Top-1={top10_cos_ids[0]} | "
            f"Top1_match={top1_match} | Top5_match={top5_match} | Top10_match={top10_match} | "
            f"max|cos-dot|={diff_cos_dot:.2e} | max|euc-sqrt(2(1-cos))|={diff_euc_formula:.2e}"
        )

    # 7. Step 5: Compare Phase 4 Top-1 vs Phase 5 Top-1
    print(f"\n[STEP 5: Comparison of Phase 4 and Phase 5 JSON Artifacts]")
    for i, q in enumerate(queries_def):
        qid = q["query_id"]
        p4_top1 = phase4_json["queries"][i]["top_5"][0]["id"]
        p5_top1_cos = phase5_json["query_evaluations"][i]["rankings_k5"]["cosine"][0]["record_id"]
        p5_top1_euc = phase5_json["query_evaluations"][i]["rankings_k5"]["euclidean"][0]["record_id"]
        p5_top1_dot = phase5_json["query_evaluations"][i]["rankings_k5"]["dot_product"][0]["record_id"]

        print(f"  {qid}: Phase 4 Top-1 = {p4_top1} | Phase 5 Top-1 = {p5_top1_cos} (Cos) / {p5_top1_dot} (Dot) / {p5_top1_euc} (Euc) | Matches: {p4_top1 == p5_top1_cos}")


if __name__ == "__main__":
    main()
