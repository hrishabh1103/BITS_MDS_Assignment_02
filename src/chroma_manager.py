"""Persistent ChromaDB vector database manager for the Vehicle Troubleshooting Assistant.

Handles local database persistence, collection lifecycle, batch ingestion,
record updates, deletions, and low-level collection queries using the
sentence-transformers embedding function.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import chromadb
from chromadb.config import Settings
import numpy as np

from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.embeddings import ChromaEmbeddingAdapter, EmbeddingManager
from src.utils import setup_logger

logger = setup_logger("chroma_manager")


class ChromaDBManager:
    """Manages persistent ChromaDB storage and operations."""

    def __init__(
        self,
        persist_dir: Optional[Union[str, Path]] = None,
        collection_name: str = CHROMA_COLLECTION_NAME,
        embedding_manager: Optional[EmbeddingManager] = None,
        distance_metric: str = "cosine",
    ):
        self.persist_dir = Path(persist_dir or CHROMA_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.distance_metric = distance_metric

        # Initialize Embedding Manager & Chroma Adapter
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.embedding_adapter = ChromaEmbeddingAdapter(self.embedding_manager)

        # Initialize Persistent Chroma Client
        logger.info(f"Connecting to persistent ChromaDB at '{self.persist_dir}'...")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False, is_persistent=True),
        )

        # Initialize Collection
        self.collection = self.get_or_create_collection(
            name=self.collection_name,
            distance_metric=self.distance_metric,
        )

    def get_or_create_collection(
        self,
        name: Optional[str] = None,
        distance_metric: Optional[str] = None,
    ) -> chromadb.Collection:
        """Retrieves or creates a ChromaDB collection with configured embedding adapter."""
        col_name = name or self.collection_name
        metric = distance_metric or self.distance_metric
        logger.info(f"Opening ChromaDB collection '{col_name}' (space='{metric}')...")

        collection = self.client.get_or_create_collection(
            name=col_name,
            embedding_function=self.embedding_adapter,
            metadata={"hnsw:space": metric},
        )
        return collection

    def get_count(self, collection_name: Optional[str] = None) -> int:
        """Returns the total number of documents in the collection."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        return col.count()

    def add_records_batch(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[Union[np.ndarray, List[List[float]]]] = None,
        batch_size: int = 500,
        collection_name: Optional[str] = None,
    ) -> int:
        """Adds documents in chunks to prevent memory bottlenecks or request payload limits."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        total = len(ids)
        inserted = 0

        # Convert numpy embeddings to list of floats if provided
        emb_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings

        logger.info(f"Inserting {total} documents into '{col.name}' in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            chunk_end = min(i + batch_size, total)
            chunk_ids = ids[i:chunk_end]
            chunk_docs = documents[i:chunk_end]
            chunk_metas = metadatas[i:chunk_end]
            chunk_embs = emb_list[i:chunk_end] if emb_list is not None else None

            if chunk_embs is not None:
                col.upsert(
                    ids=chunk_ids,
                    documents=chunk_docs,
                    metadatas=chunk_metas,
                    embeddings=chunk_embs,
                )
            else:
                col.upsert(
                    ids=chunk_ids,
                    documents=chunk_docs,
                    metadatas=chunk_metas,
                )
            inserted += len(chunk_ids)
            logger.info(f"  Inserted chunk {i + 1}-{chunk_end} of {total} ({inserted}/{total})")

        return inserted

    def get_record_by_id(
        self,
        record_id: str,
        collection_name: Optional[str] = None,
        include_embeddings: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a single record by its ID."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        includes = ["documents", "metadatas"]
        if include_embeddings:
            includes.append("embeddings")

        result = col.get(ids=[record_id], include=includes)
        if result and result["ids"] and len(result["ids"]) > 0:
            rec = {
                "id": result["ids"][0],
                "document": result["documents"][0] if result["documents"] else "",
                "metadata": result["metadatas"][0] if result["metadatas"] else {},
            }
            if include_embeddings and result.get("embeddings") is not None:
                rec["embedding"] = result["embeddings"][0]
            return rec
        return None

    def update_record(
        self,
        record_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        collection_name: Optional[str] = None,
    ) -> bool:
        """Updates document content, metadata, or embedding for an existing ID."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        kwargs: Dict[str, Any] = {"ids": [record_id]}
        if document is not None:
            kwargs["documents"] = [document]
        if metadata is not None:
            kwargs["metadatas"] = [metadata]
        if embedding is not None:
            kwargs["embeddings"] = [embedding]

        col.update(**kwargs)
        return True

    def delete_record(
        self,
        record_id: str,
        collection_name: Optional[str] = None,
    ) -> bool:
        """Deletes a record by ID."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        col.delete(ids=[record_id])
        return True

    def query(
        self,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Queries the collection using semantic similarity and optional metadata filters."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        kwargs: Dict[str, Any] = {
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if query_embedding is not None:
            kwargs["query_embeddings"] = [query_embedding]
        elif query_text is not None:
            kwargs["query_texts"] = [query_text]
        else:
            raise ValueError("Either query_text or query_embedding must be supplied.")

        if where:
            kwargs["where"] = where
        if where_document:
            kwargs["where_document"] = where_document

        return col.query(**kwargs)

    def peek(self, limit: int = 5, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Peeks at the top records in the collection."""
        col = self.collection if (collection_name is None or collection_name == self.collection_name) else self.client.get_collection(collection_name)
        return col.peek(limit=limit)

    def reset_collection(self, collection_name: Optional[str] = None) -> None:
        """Deletes and recreates a collection."""
        name = collection_name or self.collection_name
        logger.warning(f"Resetting collection '{name}'...")
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
        self.collection = self.get_or_create_collection(name)
