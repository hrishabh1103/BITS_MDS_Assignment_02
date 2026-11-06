"""Configuration settings for the Vehicle Troubleshooting Assistant.

Loads settings from environment variables and sets sensible defaults for
ChromaDB, embedding models, LLM providers, and file paths.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
QUERIES_DIR = DATA_DIR / "queries"

DATABASE_DIR = BASE_DIR / "database"
CHROMA_PERSIST_DIR = DATABASE_DIR / "chroma_db"

EXPERIMENTS_DIR = BASE_DIR / "experiments"
RESULTS_DIR = EXPERIMENTS_DIR / "results"
QUERY_RESULTS_DIR = EXPERIMENTS_DIR / "query_results"
METRIC_COMPARISON_DIR = EXPERIMENTS_DIR / "metric_comparison"
RAG_EVALUATION_DIR = EXPERIMENTS_DIR / "rag_evaluation"

DOCS_DIR = BASE_DIR / "docs"

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Embedding Configuration
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "vehicle_troubleshooting_kb")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # 'ollama' or 'external'
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "")
EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL", "https://api.openai.com/v1")
EXTERNAL_MODEL_NAME = os.getenv("EXTERNAL_MODEL_NAME", "gpt-4o-mini")

# Data files
PROCESSED_DATASET_FILE = PROCESSED_DATA_DIR / "vehicle_troubleshooting_dataset.json"
QUERIES_FILE = QUERIES_DIR / "assignment_queries.json"
