# Simple MCP Server

A minimal, easy-to-understand MCP (Model Context Protocol) server for Claude Desktop with **tools** and **resources**.

## 📋 Tools (4 operations)

| Tool | Purpose | Persistent? |
|------|---------|------------|
| **save_memory** | Save key-value pairs | ✅ Yes (JSON file) |
| **load_memory** | Load all saved memories | ✅ Yes (from JSON file) |
| **get_time** | Get current date/time | ❌ No |
| **calculate** | Math operations (add/subtract/multiply/divide) | ❌ No |

## 📁 Resources (4 data sources)

| Resource | Purpose |
|----------|---------|
| **memory://data** | View all saved memories as JSON |
| **file://memory.json** | Direct access to memory.json file |
| **file://cosmin.json** | User profile data |
| **status://server** | Server status and statistics |

## 📁 Files

- **server.py** - The MCP server implementation with tools & resources
- **requirements.txt** - Python dependencies (`mcp[cli]`)
- **cosmin.json** - Sample data file exposed as a resource
- **memory.json** - Auto-created when you save memories
- **SETUP.md** - Detailed setup and debugging
- **test_tools.py** - Quick tool verification script

## 🚀 Setup & Running

### Installation (One-time)
```bash
cd /Users/cosmin/Projects/MCP/simpleexample
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Run the Server Locally

**Option 1: For Claude Desktop (normal mode)**
```bash
source .venv/bin/activate
python3 server.py
```
Keep this running in a terminal. Claude Desktop will connect automatically.

**Option 2: For Development & Testing (with Inspector)**
```bash
source .venv/bin/activate
mcp dev server.py
```
Opens interactive MCP Inspector at `http://localhost:5173` - test tools & resources live

**Option 3: Just run the server**
```bash
source .venv/bin/activate
mcp run server.py
```

### Configure Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

**Then:**
1. Save the config file
2. Fully restart Claude Desktop (close and reopen)
3. Server should connect automatically

## 🧪 Testing in Claude Desktop

### Testing Tools (Actions)
Ask Claude to **perform actions**:

```
"Save to memory: project = MCP Server"
→ Executes: save_memory tool → Saves to memory.json

"What's saved in my memory?"
→ Executes: load_memory tool → Reads from memory.json

"Calculate 25 multiply 4"
→ Executes: calculate tool → Returns 100

"What time is it?"
→ Executes: get_time tool → Returns timestamp
```

### Testing Resources (Reading)
Ask Claude to **view data**:

```
"Show me the cosmin profile"
→ Reads: file://cosmin.json resource → Returns JSON content

"What's in the memory store?"
→ Reads: memory://data resource → Returns all saved memories

"Show server status"
→ Reads: status://server resource → Returns server info

"What resources are available?"
→ Lists all exposed resources
```

### Tools + Resources Together 🚀
**The power of MCP:** Tools and resources work **together seamlessly**:

```
Workflow:
1. User: "Save my API key"
   → Tool: save_memory executes → Stores in memory.json

2. User: "Show me everything I saved"
   → Resource: load_memory tool + memory://data resource
   → Can read via tool OR resource

3. User: "What's my profile and settings?"
   → Resource: file://cosmin.json (profile data)
   → Tool: load_memory (settings)
   → Returns both in one response

4. User: "Calculate 100 * 3, then save result"
   → Tool: calculate executes → Returns 300
   → Tool: save_memory executes → Saves result
   → Status: Resource shows calculation in stats
```

**Key Differences:**
- **Tools** (4): Execute actions - save data, calculate, get time
- **Resources** (4): Read data - memory.json, cosmin.json, server status

**Best Practices:**
- Use **Tools** for: Creating, modifying, computing
- Use **Resources** for: Viewing, inspecting, reading
- Combine both for: Rich workflows (save → view → analyze)

## 💾 Memory Storage

All saved memories go to: `./memory.json` (in project root)

View anytime:
```bash
cat /Users/cosmin/Projects/MCP/simpleexample/memory.json
```

## 🏗️ Architecture

```
Claude Desktop
      ↓
   (stdio)
      ↓
  MCP Server (server.py)
      ├── Tools (4)
      │   ├── save_memory → memory.json ✅ persistent
      │   ├── load_memory ← memory.json ✅ persistent
      │   ├── get_time → system clock ⚡ stateless
      │   └── calculate → compute ⚡ stateless
      │
      └── Resources (4)
          ├── memory://data → memory.json ✅ persistent
          ├── file://memory.json → memory.json ✅ persistent
          ├── file://cosmin.json → cosmin.json ✅ persistent
          └── status://server → server stats ⚡ stateless
```

## 🔧 Customization

Want to add more tools? Edit `server.py`:
1. Add tool implementation function
2. Add Tool to `@server.list_tools()` function
3. Add case to `@server.call_tool()` function
4. Restart Claude Desktop

Want to add more resources? Edit `server.py`:
1. Add Resource to `@server.list_resources()` function
2. Add case to `@server.read_resource()` function
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
