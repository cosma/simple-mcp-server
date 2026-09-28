#!/usr/bin/env python3
"""
Simple MCP Server with Tools and Resources

ARCHITECTURE:
- TOOLS (5): Functions that An MCP client can CALL to perform actions
  · save_memory, load_memory, get_time, calculate, get_weather

- RESOURCES (4): Data that An MCP client can READ to inspect state
  · memory://data, file://memory.json, status://server

FLOW:
1. An MCP client connects to this server via stdio
2. Server advertises what it can do (tools + resources)
3. The MCP client asks: "call this tool" or "read this resource"
4. Server executes and returns result
5. The client formats the result for the user
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

# Persistent storage file for save_memory and load_memory tools
MEMORY_FILE = Path(__file__).parent / "memory.json"

# --- Helpers for persistent memory storage ---
def load_memory():
    """Read memory.json file, return as dict."""
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        return json.loads(content) if content else {}
    return {}

def save_memory(data):
    """Write dict to memory.json file."""
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

# Initialize the MCP server
server = Server("simple-mcp-server")

# ============================================================================
# TOOLS - Functions that An MCP client can CALL to perform actions
# ============================================================================
# Each function receives a dict of arguments and returns a string result.
# The returned string is sent back to Claude, which formats it for the user.

async def save_memory_tool(args):
    """TOOL: Save a key-value pair to persistent memory.json file."""
    mem = load_memory()
    mem[args["key"]] = args["value"]
    save_memory(mem)
    return f"Saved {args['key']}"

async def load_memory_tool(args):
    """TOOL: Load and return all saved memories from memory.json file."""
    return json.dumps(load_memory(), indent=2)

async def get_time_tool(args):
    """TOOL: Return the current date and time."""
    return datetime.now().isoformat()

async def calculate_tool(args):
    """TOOL: Perform math operation (add/subtract/multiply/divide)."""
    a, b = float(args["a"]), float(args["b"])
    op = args["operation"]
    r = a + b if op == "add" else a - b if op == "subtract" else a * b if op == "multiply" else a / b
    return f"{a} {op} {b} = {r}"

async def get_weather_tool(args):
    """TOOL: Fetch current weather for a city from wttr.in (free API, no key needed)."""
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

# --- Tool Handler: Advertisement ---
# When the client asks "what tools do you have?", this handler replies with
# a list of all available tools, their descriptions, and what arguments they need.
@server.list_tools()
async def list_tools():
    """Advertisement: Tell Claude about all available tools."""
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

# --- Tool Handler: Execution ---
# When the client asks to call a tool, this handler:
# 1. Routes the tool name to the right function (the router dict)
# 2. Calls that function with the arguments the client extracted
# 3. Wraps the result in TextContent format (required by MCP SDK)
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool: route to implementation, call it, wrap the result."""
    # Router: maps tool names to their implementation functions
    tools_impl = {
        "save_memory": save_memory_tool,
        "load_memory": load_memory_tool,
        "get_time": get_time_tool,
        "calculate": calculate_tool,
        "get_weather": get_weather_tool,
    }
    # Call the function and get the result string
    result = await tools_impl[name](arguments or {})
    # Wrap result in TextContent (MCP SDK requirement for tools)
    return [TextContent(type="text", text=result)]

# ============================================================================
# RESOURCES - Data that An MCP client can READ to inspect state (not execute actions)
# ============================================================================
# Resources are read-only; Claude can view them but not modify them.
# Each resource has a URI like "memory://data" or "file://cosmin.json".

# --- Resource Handler: Advertisement ---
# When the client asks "what resources do you have?", this handler replies with
# a list of all available resources, their URIs, descriptions, and MIME types.
@server.list_resources()
async def list_resources():
    """Advertisement: Tell Claude about all available resources."""
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
            "uri": "status://server",
            "name": "Server Status",
            "description": "Current server information and stats",
            "mimeType": "text/plain"
        },
    ]

# --- Resource Handler: Reading ---
# When the client asks to read a resource, this handler:
# 1. Normalizes the URI (removes trailing slashes from file:// URIs)
# 2. Matches it against known resources
# 3. Returns the content as a string
@server.read_resource()
async def read_resource(uri) -> str:
    """Read a resource: match URI to content, return as string."""
    # Normalize URI: file://cosmin.json/ becomes file://cosmin.json
    key = str(uri).rstrip("/")

    # RESOURCE 1 & 2: Memory data (two ways to access the same file)
    if key in ("memory://data", "file://memory.json"):
        return json.dumps(load_memory(), indent=2)

    # RESOURCE 3: Server status and statistics
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
        # Claude asked for a resource that doesn't exist
        return f"Unknown resource: {key}"

# ============================================================================
# SERVER STARTUP
# ============================================================================
async def main():
    """Start the MCP server on stdio (standard input/output)."""
    # stdio_server() handles the MCP protocol over stdin/stdout
    # This is how Claude Desktop communicates with this server
    async with stdio_server() as (reader, writer):
        # server.run() starts listening for requests from Claude Desktop
        await server.run(reader, writer, server.create_initialization_options())

if __name__ == "__main__":
    # Run the async server
    asyncio.run(main())
