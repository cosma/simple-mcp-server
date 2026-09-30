"""Memory store: persistent key-value storage in memory.json and its resource."""

import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent.parent / "memory.json"


def load_memory() -> dict:
    """Read memory.json file, return as dict."""
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        return json.loads(content) if content else {}
    return {}


def save_memory(data: dict) -> None:
    """Write dict to memory.json file."""
    MEMORY_FILE.write_text(json.dumps(data, indent=2))


def read_memory_data() -> str:
    """Content for the memory://data and file://memory.json resources."""
    return json.dumps(load_memory(), indent=2)
