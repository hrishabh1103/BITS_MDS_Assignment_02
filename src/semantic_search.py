"""Semantic search and retrieval engine for the Vehicle Troubleshooting Assistant.

Performs natural language vector search over ChromaDB with configurable top-K,
distance calculations, source citations, and metadata filtering.
"""

from typing import Any, Dict, List, Optional
from src.chroma_manager import ChromaDBManager
from src.embeddings import EmbeddingManager
from src.utils import setup_logger

logger = setup_logger("semantic_search")


class SemanticSearchEngine:
    """Provides high-level natural language retrieval with distance and attribution."""

    def __init__(
        self,
        chroma_manager: Optional[ChromaDBManager] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
    ):
        self.chroma_manager = chroma_manager or ChromaDBManager()
        self.embedding_manager = embedding_manager or self.chroma_manager.embedding_manager

    def search(
        self,
        query: str,
        top_k: int = 5,
        query_id: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Executes a semantic similarity query against the persistent ChromaDB collection.

        Args:
            query: Natural language troubleshooting question or symptom description.
            top_k: Number of most similar records to retrieve.
            query_id: Optional identifier for the query (e.g. 'Q01').
            where: Optional metadata filter dict (e.g. {"vehicle_system": "engine_and_transmission"}).
            where_document: Optional document text filter dict.

        Returns:
            List of structured result dictionaries ordered by relevance rank (1..K).
        """
        if not query or not query.strip():
            logger.warning("Empty query received in semantic search.")
            return []

        if top_k <= 0:
            raise ValueError(f"top_k must be a positive integer, got {top_k}")

        query_text = query.strip()
        logger.info(f"Executing semantic search for query [{query_id or 'adhoc'}]: '{query_text[:80]}...' (top_k={top_k})")

        # ChromaDB query using embedding adapter
        raw_results = self.chroma_manager.query(
            query_text=query_text,
            n_results=top_k,
            where=where,
            where_document=where_document,
        )

        formatted_results: List[Dict[str, Any]] = []

        if not raw_results or not raw_results.get("ids") or len(raw_results["ids"][0]) == 0:
            logger.info("No matching records found for query.")
            return []

        ids = raw_results["ids"][0]
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]

        for rank_idx, rec_id in enumerate(ids):
            doc = documents[rank_idx] if rank_idx < len(documents) else ""
            meta = metadatas[rank_idx] if rank_idx < len(metadatas) else {}
            dist = float(distances[rank_idx]) if rank_idx < len(distances) else 0.0

            # Convert distance to similarity score:
            # In ChromaDB with cosine distance, distance = 1 - cosine_similarity
            # Thus cosine_similarity = 1 - distance
            similarity = max(0.0, 1.0 - dist)

            # Generate concise excerpt from problem description or document
            excerpt = doc.split("\n")[0] if "\n" in doc else doc
            for line in doc.split("\n"):
                if line.startswith("Problem Description:"):
                    excerpt = line.replace("Problem Description:", "").strip()
                    break

            item = {
                "query_id": query_id,
                "rank": rank_idx + 1,
                "id": rec_id,
                "record_id": rec_id,
                "distance": round(dist, 4),
                "raw_distance": round(dist, 6),
                "similarity_score": round(similarity, 4),
                "title": meta.get("title", ""),
                "excerpt": excerpt[:250] + ("..." if len(excerpt) > 250 else ""),
                "document": doc,
                "metadata": meta,
                "diagnostic_codes": meta.get("diagnostic_codes", ""),
                "vehicle_system": meta.get("vehicle_system", ""),
                "severity": meta.get("severity", ""),
                "source": meta.get("source", ""),
                "source_url": meta.get("source_url", ""),
            }
            formatted_results.append(item)

        logger.info(f"Retrieved {len(formatted_results)} results for [{query_id or 'adhoc'}].")
        return formatted_results


if __name__ == "__main__":
    engine = SemanticSearchEngine()
    results = engine.search("engine overheating with white smoke from exhaust", top_k=3)
    print(f"Results retrieved: {len(results)}")
    for r in results:
        print(f"Rank {r['rank']}: {r['id']} (Distance: {r['distance']}) - {r['title']}")

