from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
import json
from pathlib import Path

STATS_PATH = Path(__file__).parent / "stats.json"

DEFAULT_STATS = {
    "bj_user_wins": 0,
    "bj_cpu_wins": 0,
    "bj_blackjacks": 0,
    "bj_best_streak": 0,
}


def load_stats() -> Dict[str, Any]:
    if not STATS_PATH.exists():
        return DEFAULT_STATS.copy()
    try:
        return {**DEFAULT_STATS, **json.loads(STATS_PATH.read_text(encoding="utf-8"))}
    except Exception:
        return DEFAULT_STATS.copy()


def save_stats(stats: Dict[str, Any]) -> None:
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def inc(stats: Dict[str, Any], key: str, n: int = 1) -> None:
    stats[key] = int(stats.get(key, 0)) + n


def setmax(stats: Dict[str, Any], key: str, v: int) -> None:
    cur = stats.get(key)
    if cur is None or v > cur:
        stats[key] = v
