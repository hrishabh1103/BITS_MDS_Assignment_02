#!/usr/bin/env python3
"""Builds and persists the ChromaDB vector database for the Vehicle Troubleshooting Assistant.

Loads the validated dataset, computes 384-dimensional dense embeddings in batches
using sentence-transformers/all-MiniLM-L6-v2, and indexes documents and metadata
into the persistent ChromaDB local storage.

Usage:
    python scripts/build_database.py [--rebuild] [--batch-size 500]
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.chroma_manager import ChromaDBManager
from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR, PROCESSED_DATASET_FILE
from src.dataset_loader import load_processed_dataset
from src.embeddings import EmbeddingManager, create_record_text, format_metadata_for_chroma
from src.utils import setup_logger

logger = setup_logger("build_database_script")


def build_database(
    rebuild: bool = False,
    batch_size: int = 500,
) -> int:
    """Builds and indexes the complete vehicle troubleshooting collection."""
    start_time = time.time()
    logger.info("Initializing ChromaDB build pipeline...")

    # Step 1: Load validated dataset
    records = load_processed_dataset(PROCESSED_DATASET_FILE)
    total_records = len(records)
    logger.info(f"Loaded {total_records} validated records from {PROCESSED_DATASET_FILE}")

    if total_records < 5000:
        logger.error(f"Dataset has {total_records} records, below the 5,000 requirement.")
        sys.exit(1)

    # Step 2: Initialize Embedding and Chroma Managers
    embedding_manager = EmbeddingManager()
    chroma_manager = ChromaDBManager(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_manager=embedding_manager,
    )

    # Step 3: Check existing database state
    existing_count = chroma_manager.get_count()
    logger.info(f"Existing records in collection '{CHROMA_COLLECTION_NAME}': {existing_count}")

    if existing_count == total_records and not rebuild:
        logger.info(f"Collection already contains all {total_records} records. Verification complete.")
        print(f"\n[OK] Collection '{CHROMA_COLLECTION_NAME}' already populated with {existing_count} records.")
        return existing_count

    if rebuild and existing_count > 0:
        logger.warning(f"Rebuild requested. Clearing existing {existing_count} records...")
        chroma_manager.reset_collection()

    # Step 4: Batch preparation and insertion
    logger.info(f"Beginning batch vectorization and ingestion (batch_size={batch_size})...")
    inserted_total = 0

    for i in range(0, total_records, batch_size):
        chunk_records = records[i : i + batch_size]
        chunk_ids = [r["id"] for r in chunk_records]
        chunk_texts = [create_record_text(r) for r in chunk_records]
        chunk_metas = [format_metadata_for_chroma(r) for r in chunk_records]

        # Generate embeddings for current chunk
        chunk_embeddings = embedding_manager.embed_documents(
            chunk_texts,
            batch_size=64,
            show_progress_bar=False,
            normalize=True,
        )

        # Upsert into ChromaDB
        chroma_manager.add_records_batch(
            ids=chunk_ids,
            documents=chunk_texts,
            metadatas=chunk_metas,
            embeddings=chunk_embeddings,
            batch_size=batch_size,
        )
        inserted_total += len(chunk_ids)
        percent = (inserted_total / total_records) * 100
        logger.info(f"Progress: {inserted_total}/{total_records} records inserted ({percent:.1f}%)")

    # Step 5: Verification
    final_count = chroma_manager.get_count()
    duration = time.time() - start_time
    logger.info(f"Indexing completed in {duration:.2f} seconds. Final count: {final_count}")

    if final_count != total_records:
        logger.error(f"Mismatch: Expected {total_records} records, found {final_count} in ChromaDB.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("CHROMADB PERSISTENT INDEX BUILD SUMMARY")
    print("=" * 60)
    print(f"Collection Name:          {CHROMA_COLLECTION_NAME}")
    print(f"Persist Directory:        {CHROMA_PERSIST_DIR}")
    print(f"Embedding Model:          {embedding_manager.model_name}")
    print(f"Vector Dimensions:        {embedding_manager.dimension}")
    print(f"Total Records Indexed:    {final_count}")
    print(f"Build Duration:           {duration:.2f} seconds")
    print("Status:                   PERSISTENT & VERIFIED")

    # Step 6: Quick Sanity Verification Query
    logger.info("Executing sample verification query: 'brake pedal feels spongy'...")
    results = chroma_manager.query(query_text="brake pedal feels spongy", n_results=1)
    if results and results.get("ids") and len(results["ids"][0]) > 0:
        top_id = results["ids"][0][0]
        top_dist = results["distances"][0][0]
        top_title = results["metadatas"][0][0].get("title", "Unknown")
        print(f"\nSample Search Test:")
        print(f"  Top Match ID:   {top_id}")
        print(f"  Distance:       {top_dist:.4f}")
        print(f"  Title:          {top_title}")
    else:
        logger.error("Verification query returned no results!")
        sys.exit(1)

    return final_count


def main():
    parser = argparse.ArgumentParser(description="Build persistent ChromaDB for vehicle troubleshooting.")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild existing collection from scratch.")
    parser.add_argument("--batch-size", type=int, default=500, help="Ingestion chunk size (default: 500).")
    args = parser.parse_args()

    build_database(rebuild=args.rebuild, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
