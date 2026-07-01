import json
import os
from typing import Any, Dict

from src.utils import logger


def save_data(data: Dict[str, Any], filename: str = "data.json") -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.log(f"Failed to save data: {e}")

def load_data(filename: str = "data.json") -> Dict[str, Any]:
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    except (json.JSONDecodeError, OSError):
        return {}