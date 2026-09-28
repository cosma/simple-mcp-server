#!/usr/bin/env python3
import json
import asyncio
from datetime import datetime
from pathlib import Path

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

MEMORY_FILE = Path(__file__).parent / "memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        return json.loads(content) if content else {}
    return {}

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

server = Server("simple-mcp-server")

# Tool implementations
async def save_memory_tool(args):
    mem = load_memory()
    mem[args["key"]] = args["value"]
    save_memory(mem)
    return f"Saved {args['key']}"

async def load_memory_tool(args):
    return json.dumps(load_memory(), indent=2)

async def get_time_tool(args):
    return datetime.now().isoformat()

async def calculate_tool(args):
    a, b = float(args["a"]), float(args["b"])
    op = args["operation"]
    r = a + b if op == "add" else a - b if op == "subtract" else a * b if op == "multiply" else a / b
    return f"{a} {op} {b} = {r}"

async def get_weather_tool(args):
    city = args["city"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"https://wttr.in/{city}", params={"format": "j1"})
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPStatusError:
        return f"Could not find weather for '{city}'."
    except httpx.RequestError as e:
        return f"Weather service unreachable: {e}"

    now = data["current_condition"][0]
    area = data["nearest_area"][0]
    place = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
    return (
        f"{place}: {now['weatherDesc'][0]['value'].strip()}, "
        f"{now['temp_C']}C (feels like {now['FeelsLikeC']}C), "
        f"humidity {now['humidity']}%, wind {now['windspeedKmph']} km/h"
    )

# Tool handlers
@server.list_tools()
async def list_tools():
    return [
        {
            "name": "save_memory",
            "description": "Save key-value to memory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"]
            }
        },
        {
            "name": "load_memory",
            "description": "Load saved memories",
            "inputSchema": {"type": "object"}
        },
        {
            "name": "get_time",
            "description": "Get current time",
            "inputSchema": {"type": "object"}
        },
        {
            "name": "calculate",
            "description": "Do math operations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    }
                },
                "required": ["a", "b", "operation"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. Bucharest or London"
                    }
                },
                "required": ["city"]
            }
        },
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    tools_impl = {
        "save_memory": save_memory_tool,
        "load_memory": load_memory_tool,
        "get_time": get_time_tool,
        "calculate": calculate_tool,
        "get_weather": get_weather_tool,
    }
    result = await tools_impl[name](arguments or {})
    return [TextContent(type="text", text=result)]

# Resource handlers
@server.list_resources()
async def list_resources():
    return [
        {
            "uri": "memory://data",
            "name": "Memory Store",
            "description": "Current memory.json file with all saved key-value pairs",
            "mimeType": "application/json"
        },
        {
            "uri": "file://memory.json",
            "name": "Memory File",
            "description": "Direct path to memory.json in project root",
            "mimeType": "application/json"
        },
        {
            "uri": "file://cosmin.json",
            "name": "Cosmin Profile",
            "description": "User profile and information",
            "mimeType": "application/json"
        },
        {
            "uri": "status://server",
            "name": "Server Status",
            "description": "Current server information and stats",
            "mimeType": "text/plain"
        },
    ]

@server.read_resource()
async def read_resource(uri) -> str:
    key = str(uri).rstrip("/")

    if key in ("memory://data", "file://memory.json"):
        return json.dumps(load_memory(), indent=2)

    elif key == "file://cosmin.json":
        cosmin_file = Path(__file__).parent / "cosmin.json"
        return cosmin_file.read_text() if cosmin_file.exists() else "{}"

    elif key == "status://server":
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
"""

    else:
        return f"Unknown resource: {key}"

async def main():
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
