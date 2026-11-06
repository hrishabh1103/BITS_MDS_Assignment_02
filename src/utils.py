"""General utilities for logging, JSON/JSONL serialization, and directory management."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List


def setup_logger(name: str = "vehicle_assistant", level: int = logging.INFO) -> logging.Logger:
    """Configures a standardized console logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def load_json(file_path: Path) -> Any:
    """Loads JSON data from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, file_path: Path, indent: int = 2) -> None:
    """Saves data to a JSON file, ensuring parent directory exists."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Loads a JSONL file into a list of dictionaries."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(records: List[Dict[str, Any]], file_path: Path) -> None:
    """Saves a list of dictionaries to a JSONL file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
