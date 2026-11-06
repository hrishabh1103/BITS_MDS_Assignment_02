"""Text embedding generator and model manager for the Vehicle Troubleshooting Assistant.

Utilizes Sentence-Transformers (sentence-transformers/all-MiniLM-L6-v2) to produce
dense 384-dimensional vector embeddings for both troubleshooting documents and
natural language queries. Provides batch processing, text formatting, and
ChromaDB-compatible embedding function adapters.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# Ensure fast offline loading from local cache
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from chromadb import Documents, EmbeddingFunction, Embeddings
from src.config import DEFAULT_EMBEDDING_MODEL, EMBEDDING_DEVICE
from src.utils import setup_logger

logger = setup_logger("embeddings")


def create_record_text(record: Dict[str, Any]) -> str:
    """Creates a structured text representation of a troubleshooting record for embedding.

    Concatenates diagnostic title, codes, system category, failure description,
    observed symptoms, probable root causes, diagnostic steps, and repair actions.
    Omits database IDs, raw URLs, or non-technical metadata.
    """
    parts = []

    title = record.get("title")
    if title:
        parts.append(f"Title: {title.strip()}")

    codes = record.get("diagnostic_codes")
    if codes:
        codes_str = ", ".join(codes) if isinstance(codes, list) else str(codes)
        parts.append(f"Diagnostic Codes: {codes_str}")

    system = record.get("vehicle_system")
    if system:
        parts.append(f"Vehicle System: {system.replace('_', ' ').title()}")

    desc = record.get("problem_description")
    if desc:
        parts.append(f"Problem Description: {desc.strip()}")

    symptoms = record.get("symptoms")
    if symptoms:
        symptoms_str = "; ".join(symptoms) if isinstance(symptoms, list) else str(symptoms)
        parts.append(f"Symptoms: {symptoms_str}")

    causes = record.get("possible_causes")
    if causes:
        causes_str = "; ".join(causes) if isinstance(causes, list) else str(causes)
        parts.append(f"Possible Causes: {causes_str}")

    steps = record.get("diagnostic_steps")
    if steps:
        steps_str = " ".join(steps) if isinstance(steps, list) else str(steps)
        parts.append(f"Diagnostic Steps: {steps_str}")

    actions = record.get("recommended_actions")
    if actions:
        actions_str = " ".join(actions) if isinstance(actions, list) else str(actions)
        parts.append(f"Recommended Actions: {actions_str}")

    return "\n".join(parts)


def format_metadata_for_chroma(record: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
    """Transforms record metadata into types natively supported by ChromaDB.

    ChromaDB metadata supports str, int, float, and bool. Lists and nested dicts
    are serialized into comma-separated strings.
    """
    metadata: Dict[str, Union[str, int, float, bool]] = {}

    metadata["id"] = str(record.get("id", ""))
    metadata["title"] = str(record.get("title", ""))
    metadata["vehicle_system"] = str(record.get("vehicle_system", ""))
    metadata["severity"] = str(record.get("severity", "medium"))
    metadata["vehicle_type"] = str(record.get("vehicle_type", "passenger_car_and_light_truck"))
    metadata["source"] = str(record.get("source", ""))
    metadata["source_url"] = str(record.get("source_url", ""))
    metadata["source_record_id"] = str(record.get("source_record_id", ""))
    metadata["data_origin"] = str(record.get("data_origin", "authentic_open_standard"))

    # Convert list fields to comma-separated strings
    codes = record.get("diagnostic_codes") or []
    metadata["diagnostic_codes"] = ", ".join(codes) if isinstance(codes, list) else str(codes)

    symptoms = record.get("symptoms") or []
    metadata["symptoms"] = "; ".join(symptoms) if isinstance(symptoms, list) else str(symptoms)

    causes = record.get("possible_causes") or []
    metadata["possible_causes"] = "; ".join(causes) if isinstance(causes, list) else str(causes)

    return metadata


class EmbeddingManager:
    """Manages model loading, document vectorization, and query embedding."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        device: str = EMBEDDING_DEVICE,
    ):
        self.model_name = model_name
        self.device = device
        logger.info(f"Loading embedding model '{self.model_name}' on device '{self.device}'...")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimension = self.model.get_embedding_dimension()
        else:
            self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model '{self.model_name}' loaded successfully. Embedding dimension: {self.dimension}")

    def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """Embeds a single string into a 1D vector."""
        if not text or not text.strip():
            logger.warning("Empty text passed for embedding. Using zero vector fallback.")
            return np.zeros(self.dimension, dtype=np.float32)

        embedding = self.model.encode(
            text,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embedding

    def embed_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Embeds a user query. Syntactic alias for embed_text."""
        return self.embed_text(query, normalize=normalize)

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress_bar: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        """Generates embeddings for a batch of text documents."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        # Handle any empty strings safely
        cleaned = [t if (t and t.strip()) else "empty record" for t in texts]

        embeddings = self.model.encode(
            cleaned,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )
        return embeddings

    def embed_records(
        self,
        records: List[Dict[str, Any]],
        batch_size: int = 64,
        show_progress_bar: bool = False,
        normalize: bool = True,
    ) -> Tuple[List[str], np.ndarray, List[str], List[Dict[str, Any]]]:
        """Processes a list of troubleshooting records.

        Returns:
            Tuple of (ids, embeddings_array, document_texts, metadatas)
        """
        ids = [r["id"] for r in records]
        doc_texts = [create_record_text(r) for r in records]
        metadatas = [format_metadata_for_chroma(r) for r in records]

        logger.info(f"Generating embeddings for {len(records)} records (batch_size={batch_size})...")
        embeddings = self.embed_documents(
            doc_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize=normalize,
        )
        return ids, embeddings, doc_texts, metadatas


class ChromaEmbeddingAdapter(EmbeddingFunction[Documents]):
    """Adapter class allowing ChromaDB to use our EmbeddingManager."""

    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def name(self) -> str:
        """Returns the embedding function name for ChromaDB collection metadata."""
        return self.embedding_manager.model_name

    def default_space(self) -> str:
        """Default distance metric."""
        return "cosine"

    def supported_spaces(self) -> List[str]:
        """Supported vector spaces."""
        return ["cosine", "l2", "ip"]

    def get_config(self) -> Dict[str, Any]:
        """Returns configuration dictionary for ChromaDB serialization."""
        return {
            "model_name": self.embedding_manager.model_name,
            "device": self.embedding_manager.device,
        }

    def __call__(self, input: Documents) -> Embeddings:
        """ChromaDB embedding interface: takes list of texts, returns list of float vectors."""
        embeddings = self.embedding_manager.embed_documents(list(input), normalize=True)
        return embeddings.tolist()
