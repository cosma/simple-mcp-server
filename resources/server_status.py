"""Server Status resource."""

from . import memory_store


def read_server_status() -> str:
    """Read status://server resource content."""
    mem = memory_store.load_memory()
    return f"""MCP Server Status
================
Server: simple-mcp-server
Status: Running
Protocol: stdio

Memory Stats:
- Entries: {len(mem)}
- Keys: {', '.join(mem.keys()) if mem else 'none'}
- File: {memory_store.MEMORY_FILE}

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
