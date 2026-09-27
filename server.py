#!/usr/bin/env python3
import json
import asyncio
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult, ListToolsRequest, CallToolRequestParams

MEMORY_FILE = Path(__file__).parent / "memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        return json.loads(content) if content else {}
    return {}

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

server = Server("simple-mcp")

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

# Handlers - signature: (ctx, params)
async def list_tools_handler(ctx, params):
    return ListToolsResult(tools=[
        Tool(name="save_memory", description="Save key-value to memory", inputSchema={"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}),
        Tool(name="load_memory", description="Load saved memories", inputSchema={"type": "object"}),
        Tool(name="get_time", description="Get current time", inputSchema={"type": "object"}),
        Tool(name="calculate", description="Do math operations", inputSchema={"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}, "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}}, "required": ["a", "b", "operation"]}),
    ])

async def call_tool_handler(ctx, params):
    tools_impl = {
        "save_memory": save_memory_tool,
        "load_memory": load_memory_tool,
        "get_time": get_time_tool,
        "calculate": calculate_tool,
    }
    result = await tools_impl[params.name](params.arguments or {})
    return CallToolResult(content=[TextContent(type="text", text=result)])

# Register handlers
server.add_request_handler("tools/list", ListToolsRequest, list_tools_handler)
server.add_request_handler("tools/call", CallToolRequestParams, call_tool_handler)

async def main():
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
