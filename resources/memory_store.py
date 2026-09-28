"""Memory Store resources."""

import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent.parent / "memory.json"


def load_memory() -> dict:
    """Read memory.json file, return as dict."""
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        return json.loads(content) if content else {}
    return {}


def get_memory_data_resource() -> dict:
    """Resource definition for memory://data"""
    return {
        "uri": "memory://data",
        "name": "Memory Store",
        "description": "Current memory.json file with all saved key-value pairs",
        "mimeType": "application/json"
    }


def get_memory_file_resource() -> dict:
    """Resource definition for file://memory.json"""
    return {
        "uri": "file://memory.json",
        "name": "Memory File",
        "description": "Direct path to memory.json in project root",
        "mimeType": "application/json"
    }


def read_memory_data() -> str:
    """Read memory://data resource content."""
    return json.dumps(load_memory(), indent=2)


def read_memory_file() -> str:
    """Read file://memory.json resource content."""
    return json.dumps(load_memory(), indent=2)
