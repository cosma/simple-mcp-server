"""Server Status resource."""

from .memory_store import load_memory, MEMORY_FILE


def get_server_status_resource() -> dict:
    """Resource definition for status://server"""
    return {
        "uri": "status://server",
        "name": "Server Status",
        "description": "Current server information and stats",
        "mimeType": "text/plain"
    }


def read_server_status() -> str:
    """Read status://server resource content."""
    mem = load_memory()
    return f"""MCP Server Status
================
Server: simple-mcp-server
Status: Running
Protocol: stdio

Memory Stats:
- Entries: {len(mem)}
- Keys: {', '.join(mem.keys()) if mem else 'none'}
- File: {MEMORY_FILE}

Tools Available: 5
1. save_memory   (persistent)
2. load_memory   (persistent)
3. get_time      (stateless)
4. calculate     (stateless)
5. get_weather   (network)

Prompts Available: 2
1. weather_activity_planner   (parameterized activity planning)
2. weather_alert_explainer    (parameterized alert explanation)

Resources Available: 3
1. memory://data       (memory store)
2. file://memory.json  (memory file)
3. status://server     (server status)
"""
