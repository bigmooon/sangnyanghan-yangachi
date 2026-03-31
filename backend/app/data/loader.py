from functools import lru_cache
import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load(filename: str) -> dict | list:
    path = (_DATA_DIR / filename).resolve()
    if not str(path).startswith(str(_DATA_DIR.resolve())):
        raise ValueError(f"잘못된 파일명: {filename}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache
def get_characters() -> dict[int, dict]:
    return {c["id"]: c for c in _load("characters.json")["characters"]}


@lru_cache
def get_items() -> dict[str, dict]:
    return _load("items.json")["items"]


@lru_cache
def get_events() -> list[dict]:
    return _load("events.json")["events"]
