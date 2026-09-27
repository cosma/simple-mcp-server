# Quick Start Guide

## What you have
A simple MCP server with 4 operations:
- **save_memory** - Save notes to `~/.mcp_memory.json`
- **load_memory** - Retrieve saved notes
- **get_time** - Get current time
- **calculate** - Do math (add/subtract/multiply/divide)

## Step 1: Setup (already done)
Dependencies installed in `.venv/` ✓

## Step 2: Configure Claude Desktop
Open or create: `~/Library/Application Support/Claude/claude_desktop_config.json`

Paste this:
```json
{
  "mcpServers": {
    "simple-mcp": {
      "command": "/Users/cosmin/Projects/MCP/simpleexample/.venv/bin/python",
      "args": ["/Users/cosmin/Projects/MCP/simpleexample/server.py"]
    }
  }
}
```

## Step 3: Restart Claude Desktop
Close it completely, then reopen.

## Step 4: Try it in Claude Desktop

**Save memory:**
- "Save to memory: favorite_color = blue"

**Load memory:**
- "What's saved in my memory?"

**Get time:**
- "What time is it?"

**Calculate:**
- "Calculate 10 add 5"
- "Calculate 100 divide 4"

That's it! 🎉
