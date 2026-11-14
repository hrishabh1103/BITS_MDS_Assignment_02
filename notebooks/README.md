# Jupyter Notebooks

This directory is intended for interactive exploration, prototyping, and ad-hoc vector querying.

## Available Modules for Notebook Import

All core pipeline modules can be imported directly within a notebook environment:

```python
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd().parent))

from src.chroma_manager import ChromaDBManager
from src.semantic_search import SemanticSearchEngine
from src.rag_pipeline import RAGPipeline

# Initialize manager and search
manager = ChromaDBManager()
search_engine = SemanticSearchEngine(chroma_manager=manager)

# Execute ad-hoc semantic query
results = search_engine.search("alternator charging voltage normal but battery drains", top_k=5)
for r in results:
    print(r["record_id"], r["title"], r["distance"])
```

## Running the Interactive Streamlit App

For the full interactive UI experience, run the Streamlit dashboard:

```bash
streamlit run app.py
```
