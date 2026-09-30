#!/usr/bin/env python3
"""
Simple MCP Server with Tools, Resources, and Prompts (FastMCP-style API)

- TOOLS (5): functions a client can CALL
  · save_memory, load_memory, get_time, calculate, get_weather
- RESOURCES (3): data a client can READ  (implemented in /resources)
  · memory://data, file://memory.json, status://server
- PROMPTS (2): parameterized prompt templates  (implemented in /prompts)
  · weather_activity_planner, weather_alert_explainer

Names, descriptions and argument schemas are derived from each function's
name, docstring and type hints.

Run:  python server.py        (stdio, for Claude Desktop)
      mcp dev server.py       (MCP Inspector)
"""

import json
from datetime import datetime
from typing import Literal

import httpx2
from mcp.server import MCPServer

from prompts import weather_activity_planner as activity_planner
from prompts import weather_alert_explainer as alert_explainer
from resources import memory_store, server_status

mcp = MCPServer("simple-mcp-server")


# ============================================================================
# TOOLS
# ============================================================================
@mcp.tool()
def save_memory(key: str, value: str) -> str:
    """Save a key-value pair to persistent memory."""
    data = memory_store.load_memory()
    data[key] = value
    memory_store.save_memory(data)
    return f"Saved {key}"


@mcp.tool()
def load_memory() -> str:
    """Load all saved memories."""
    return json.dumps(memory_store.load_memory(), indent=2)


@mcp.tool()
def get_time() -> str:
    """Get the current date and time (ISO format)."""
    return datetime.now().isoformat()


@mcp.tool()
def calculate(a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]) -> str:
    """Do math operations: add, subtract, multiply, divide."""
    if operation == "add":
        r = a + b
    elif operation == "subtract":
        r = a - b
    elif operation == "multiply":
        r = a * b
    else:
        if b == 0:
            return "Cannot divide by zero."
        r = a / b
    return f"{a} {operation} {b} = {r}"


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the current weather for a city (via wttr.in). City name, e.g. Bucharest or London."""
    try:
        async with httpx2.AsyncClient(timeout=15) as client:
            resp = await client.get(f"https://wttr.in/{city}", params={"format": "j1"})
        resp.raise_for_status()
        data = resp.json()
    except httpx2.HTTPStatusError:
        return f"Could not find weather for '{city}'."
    except httpx2.RequestError as e:
        return f"Weather service unreachable: {e}"

    now = data["current_condition"][0]
    area = data["nearest_area"][0]
    place = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
    return (
        f"{place}: {now['weatherDesc'][0]['value'].strip()}, "
        f"{now['temp_C']}C (feels like {now['FeelsLikeC']}C), "
        f"humidity {now['humidity']}%, wind {now['windspeedKmph']} km/h"
    )


# ============================================================================
# RESOURCES
# ============================================================================
@mcp.resource("memory://data", name="Memory Store", mime_type="application/json")
def memory_data() -> str:
    """Current memory.json file with all saved key-value pairs."""
    return memory_store.read_memory_data()


@mcp.resource("file://memory.json", name="Memory File", mime_type="application/json")
def memory_file() -> str:
    """Direct path to memory.json in project root."""
    return memory_store.read_memory_data()


@mcp.resource("status://server", name="Server Status", mime_type="text/plain")
def status() -> str:
    """Current server information and stats."""
    return server_status.read_server_status()


# ============================================================================
# PROMPTS
# ============================================================================
@mcp.prompt()
def weather_activity_planner(location: str, activity_type: str, time_horizon: str = "soon") -> str:
    """Plan outdoor activities based on weather conditions and get preparation tips."""
    return activity_planner.render(location, activity_type, time_horizon)


@mcp.prompt()
def weather_alert_explainer(alert_type: str, region: str) -> str:
    """Get simple explanations of weather alerts with safety tips and precautions."""
    return alert_explainer.render(alert_type, region)


if __name__ == "__main__":
    mcp.run()
