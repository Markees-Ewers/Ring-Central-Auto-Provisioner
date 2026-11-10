"""Persistent phone-model list management.

Author: Markees Ewers
Responsibility: Load and save the user's normalized phone-model catalog.
"""

from __future__ import annotations

import json
from pathlib import Path

CATALOG_PATH = Path(__file__).with_name("phone_models.json")

def load_models() -> list[str]:
    """Load saved model names, returning an empty list when none exist."""
    if not CATALOG_PATH.exists():
        return []
    try:
        values = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read {CATALOG_PATH.name}: {exc}") from exc
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise RuntimeError(f"{CATALOG_PATH.name} must contain a JSON list of model names.")
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


def save_models(models: list[str]) -> None:
    """Save a normalized model list."""
    try:
        CATALOG_PATH.write_text(
            json.dumps(sorted(set(model.strip() for model in models if model.strip())), indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(f"Could not save {CATALOG_PATH.name}: {exc}") from exc
