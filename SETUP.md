# Simple MCP Server Setup

This is a minimal MCP server with 4 operations:
1. **save_memory** - Save key-value pairs to a local JSON file
2. **load_memory** - Load all saved memories from file
3. **get_time** - Get current date and time
4. **calculate** - Perform basic math (add, subtract, multiply, divide)

## Installation

### 1. Install dependencies (one-time setup)
```bash
cd /Users/cosmin/Projects/MCP/simpleexample
uv venv
source .venv/bin/activate
uv pip install mcp
```


### 2. Configure Claude Desktop

Add this server to Claude Desktop's configuration:

**File location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this to your config:**
```json
{
  "mcpServers": {
    "simple-mcp-example": {
      "command": "/Users/cosmin/Projects/MCP/simpleexample/.venv/bin/python",
      "args": ["/Users/cosmin/Projects/MCP/simpleexample/server.py"]
    }
  }
}
```

If the file doesn't exist, create it with:
```json
{
  "mcpServers": {
    "simple-mcp-example": {
      "command": "python3",
      "args": ["/Users/cosmin/Projects/MCP/simpleexample/server.py"]
    }
  }
}
```

### 4. Restart Claude Desktop
Close and reopen Claude Desktop completely. The new MCP server should be available.

## Testing

In Claude Desktop, try these:

1. **Save a note:**
   - "Save this in memory: project_name = MyAwesomeApp"
   - Uses `save_memory` tool

2. **Load all memories:**
   - "What did I save in memory?"
   - Uses `load_memory` tool

3. **Get time:**
   - "What time is it?"
   - Uses `get_time` tool

4. **Calculate:**
   - "Calculate 25 multiply 4"
   - Uses `calculate` tool

## Memory Storage

All saved memories are stored in: `/Users/cosmin/Projects/MCP/simpleexample/memory.json`

You can view and edit this file directly, and changes will be available to Claude Desktop immediately.

## Debugging

If the MCP server doesn't appear in Claude Desktop:

1. Check the config file path and JSON syntax
2. Restart Claude Desktop
3. Check Claude's logs:
   - macOS: `~/Library/Logs/Claude/`

To test the server manually:
```bash
python3 server.py
```

(It will wait for stdin input from the MCP client)




# MCP Server Architecture
