# Simple MCP Server

A minimal, easy-to-understand MCP (Model Context Protocol) server for Claude Desktop with 4 operations.

## 📋 Features

| Tool | Purpose | Persistent? |
|------|---------|------------|
| **save_memory** | Save key-value pairs | ✅ Yes (JSON file) |
| **load_memory** | Load all saved memories | ✅ Yes (from JSON file) |
| **get_time** | Get current date/time | ❌ No |
| **calculate** | Math operations (add/subtract/multiply/divide) | ❌ No |

## 📁 Files

- **server.py** - The MCP server implementation (160 lines, well-commented)
- **requirements.txt** - Python dependencies (just `mcp`)
- **QUICKSTART.md** - 4-step setup guide (read this first!)
- **SETUP.md** - Detailed setup and debugging
- **test_tools.py** - Quick tool verification script

## 🚀 Quick Setup

1. **Already done:**
   ```bash
   uv venv && source .venv/bin/activate && uv pip install mcp
   ```

2. **Configure Claude Desktop:**
   - Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Add the config from `QUICKSTART.md`
   - Restart Claude Desktop

3. **Test it:**
   - In Claude, say: "Save to memory: test = works"
   - Then: "What's in my memory?"

## 💾 Memory Storage

All saved memories go to: `./memory.json` (in project root)

View anytime:
```bash
cat /Users/cosmin/Projects/MCP/simpleexample/memory.json
```

## 🔧 Customization

Want to add more tools? Edit `server.py`:
1. Add your tool to the `list_tools()` function
2. Handle it in the `call_tool()` function
3. Restart Claude Desktop

## ❓ Troubleshooting

**MCP server not showing in Claude?**
- Check config file path: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Ensure JSON syntax is valid (use a JSON validator)
- Fully restart Claude Desktop (not just window close)
- Check Claude's logs: `~/Library/Logs/Claude/`

**Dependencies not found?**
- Ensure you're using the venv: `source .venv/bin/activate`
- Or reinstall: `uv pip install mcp`

## 📚 Learning Resources

- MCP Documentation: https://modelcontextprotocol.io
- Server structure borrowed from official MCP examples
- Perfect starting point for building custom MCP tools

## 📝 Example Usage

```
User: "Save my GitHub username to memory"
→ Uses: save_memory tool
→ Saves to: ./memory.json

User: "What did I ask you to remember?"
→ Uses: load_memory tool
→ Reads from: ./memory.json

User: "What's 24 multiply 7?"
→ Uses: calculate tool
→ Returns: 168

User: "Tell me the time"
→ Uses: get_time tool
→ Returns: Current ISO timestamp
```
