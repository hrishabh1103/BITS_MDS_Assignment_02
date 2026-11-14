# Vector Database Documentation

This directory contains the persistent vector database storage for the **Vehicle Troubleshooting Assistant**.

## Overview

The system uses [ChromaDB](https://www.trychroma.com/) as an embedded, persistent vector database. Vector records are stored in a SQLite metadata file (`chroma.sqlite3`) and an index directory containing the Hierarchical Navigable Small World (HNSW) binary graph files.

## Technical Specifications

| Parameter | Value | Description |
|:---|:---|:---|
| **Collection Name** | `vehicle_troubleshooting_kb` | Primary knowledge base collection |
| **Record Count** | 9,532 | Total diagnostic trouble code (DTC) records |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` | Dense sentence representation model |
| **Embedding Dimensions** | 384 (float32) | Vector length per document |
| **Distance Metric** | Cosine (`hnsw:space = "cosine"`) | Distance metric for approximate nearest neighbor search |
| **Vector Normalization** | $L_2$ Unit Normalization ($\|\mathbf{x}\|_2 = 1.0$) | Vectors normalized before insertion |
| **Persistence Directory** | `database/chroma_db/` | Relative persistence path configured in `src/config.py` |
| **Storage Footprint** | ~180 MB | SQLite database + HNSW index files |

## Directory Structure

```
database/
├── README.md                      # This documentation file
└── chroma_db/                     # Persistent ChromaDB data
    ├── chroma.sqlite3             # Metadata, document texts, and collection registry
    └── <uuid>/                    # HNSW binary graph index and vector data
```

## How to Recreate the Database

The database can be fully reconstructed from the processed dataset (`data/processed/vehicle_troubleshooting.json`):

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Build the persistent vector database (takes ~1-2 minutes on modern CPU/GPU)
python scripts/build_database.py
```

The script will:
1. Load all 9,532 records from `data/processed/vehicle_troubleshooting.json`.
2. Generate 384-dimensional dense vector embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
3. Normalize embeddings to unit length.
4. Batch-insert records, embeddings, and metadata into the `vehicle_troubleshooting_kb` collection.
5. Verify that the collection count equals exactly 9,532.

## Inspecting the Collection

To verify the collection programmatically:

```python
from src.chroma_manager import ChromaDBManager

manager = ChromaDBManager()
print(f"Collection Name: {manager.collection_name}")
print(f"Total Records: {manager.get_count()}")

# Retrieve a single record by ID
record = manager.get_record("VTR-P00B7")
print(record["title"])
```
