"""
Shared evaluation helpers + a JSON metrics writer so the Streamlit app can
display real, saved model metrics instead of recomputing them at runtime.
"""
from __future__ import annotations

import json
from pathlib import Path

from src import config


def save_metrics(all_metrics: dict, path: Path = config.METRICS_JSON) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)


def load_metrics(path: Path = config.METRICS_JSON) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)
