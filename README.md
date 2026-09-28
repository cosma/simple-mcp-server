# Simple MCP Server

A minimal, easy-to-understand [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server for Claude Desktop with **tools**, **resources**, and **prompt templates**.

## 📋 Tools (5 operations)

| Tool | Purpose | Persistent? |
|------|---------|------------|
| **save_memory** | Save key-value pairs | ✅ Yes (JSON file) |
| **load_memory** | Load all saved memories | ✅ Yes (from JSON file) |
| **get_time** | Get current date/time | ❌ No |
| **calculate** | Math operations (add/subtract/multiply/divide) | ❌ No |
| **get_weather** | Current weather for a city (via wttr.in) | ❌ No |

## 📁 Resources (3 data sources)

| Resource | Purpose |
|----------|---------|
| **memory://data** | View all saved memories as JSON |
| **file://memory.json** | Direct access to memory.json file |
| **status://server** | Server status and statistics |

## 🎯 Prompts (2 templates)

| Prompt | Purpose | Parameters |
|--------|---------|------------|
| **weather_activity_planner** | Plan outdoor activities based on weather | location, activity_type, time_horizon (optional) |
| **weather_alert_explainer** | Explain weather alerts in simple terms | alert_type, region |

## 📁 Files & Folders

- **server.py** - Main MCP server implementation
- **requirements.txt** - Python dependencies (`mcp[cli]`)
- **memory.json** - Auto-created when you save memories
- **/prompts/** - Prompt template definitions
  - `weather_activity_planner.py` - Activity planning template
  - `weather_alert_explainer.py` - Alert explanation template
- **/resources/** - Resource implementations
  - `memory_store.py` - Memory data resources
  - `server_status.py` - Server status resource
- **test_server.py** - Comprehensive test suite for tools, resources, and prompts

## 🚀 Setup & Running

### Installation (One-time)
```bash
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
Run manually it looks like it hangs — that's correct, it's waiting for stdin
from an MCP client.

**Option 2: For Development & Testing (with Inspector)**
```bash
source .venv/bin/activate
mcp dev server.py
```
Opens interactive MCP Inspector at `http://localhost:5173` - test tools & resources live



### Configure Claude Desktop

Edit the config file (create it if it doesn't exist):

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "command": "/path/to/simple-mcp-server/.venv/bin/python",
      "args": ["/path/to/simple-mcp-server/server.py"]
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
"What's in the memory store?"
→ Reads: memory://data resource → Returns all saved memories

"Show server status"
→ Reads: status://server resource → Returns server info

"What resources are available?"
→ Lists all exposed resources
```

### Testing Prompts (Templates)
Ask Claude to **use prompt templates**:

```
"Help me plan a hiking trip to Colorado this weekend"
→ Uses: weather_activity_planner prompt template
→ Fills: location=Colorado, activity_type=hiking, time_horizon=this weekend
→ Generates: Custom prompt for activity planning

"Explain a severe thunderstorm alert for Texas"
→ Uses: weather_alert_explainer prompt template
→ Fills: alert_type=severe thunderstorm, region=Texas
→ Generates: Custom prompt explaining the weather alert

"What prompts are available?"
→ Lists all available prompt templates and their parameters
```

**How Prompts Work:**
- Prompts are **reusable templates** with parameters you fill in
- Claude asks for parameter values when needed
- Server generates a custom prompt with those values
- The prompt is then used in the conversation

### Tools + Resources + Prompts Together 🚀
**The power of MCP:** Tools and resources work **together seamlessly**:

```
Workflow:
1. User: "Save my API key"
   → Tool: save_memory executes → Stores in memory.json

2. User: "Show me everything I saved"
   → Resource: load_memory tool + memory://data resource
   → Can read via tool OR resource

3. User: "Calculate 100 * 3, then save result"
   → Tool: calculate executes → Returns 300
   → Tool: save_memory executes → Saves result
   → Status: Resource shows calculation in stats
```

**Key Differences:**
- **Tools** (5): Execute actions - save data, calculate, get time, fetch weather
- **Resources** (3): Read data - memory.json, server status
- **Prompts** (2): Reusable templates with parameters - activity planning, alert explanations

**Best Practices:**
- Use **Tools** for: Creating, modifying, computing
- Use **Resources** for: Viewing, inspecting, reading
- Use **Prompts** for: Generating custom prompts with parameters
- Combine all three for: Rich workflows (save → view → generate prompts)

## 💾 Memory Storage

All saved memories go to: `./memory.json` (in project root)

View anytime:
```bash
cat /path/to/simple-mcp-server/memory.json
```

## 🏗️ Architecture

```
Claude Desktop
      ↓
   (stdio)
      ↓
  MCP Server (server.py)
      ├── Tools (5)
      │   ├── save_memory → memory.json ✅ persistent
      │   ├── load_memory ← memory.json ✅ persistent
      │   ├── get_time → system clock ⚡ stateless
      │   ├── calculate → compute ⚡ stateless
      │   └── get_weather → wttr.in 🌐 network
      │
      ├── Resources (3) — in /resources/
      │   ├── memory://data → memory.json ✅ persistent
      │   ├── file://memory.json → memory.json ✅ persistent
      │   └── status://server → server stats ⚡ stateless
      │
      └── Prompts (2) — in /prompts/
          ├── weather_activity_planner (location, activity_type, time_horizon)
          └── weather_alert_explainer (alert_type, region)
```

## 🔧 Customization

### Adding Tools
Edit `server.py`:
1. Add tool implementation function
2. Add Tool to `@server.list_tools()` function
3. Add case to `@server.call_tool()` function
4. Restart Claude Desktop

### Adding Resources
Create new file in `/resources/`:
1. Define resource metadata and read function
2. Import in `/resources/__init__.py`
3. Add to `list_resources()` in `server.py`
4. Add case to `read_resource()` in `server.py`
5. Restart Claude Desktop

### Adding Prompts
Create new file in `/prompts/`:
1. Define prompt template with name, description, arguments
2. Add a `render()` function that fills in parameters
3. Import in `/prompts/__init__.py`
4. Add to `list_prompts()` in `server.py`
5. Add case to `get_prompt()` in `server.py`
6. Restart Claude Desktop

**Example prompt template** (`/prompts/my_template.py`):
```python
from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

MY_TEMPLATE = Prompt(
    name="my_template",
    description="My custom template",
    arguments=[
        PromptArgument(name="param1", description="First param", required=True),
        PromptArgument(name="param2", description="Second param", required=False),
    ],
)

def render(param1: str, param2: str = "default") -> GetPromptResult:
    return GetPromptResult(
        description=f"Custom prompt with {param1}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Use {param1} and {param2}"),
            )
        ],
    )
```

> ⚠️ **Use the typed MCP objects, not plain dicts.** A `PromptMessage`'s `content`
> must be a `TextContent` object — a bare string fails validation and the client
> reports *"Failed to attach prompt"* with no useful error in the logs.

## ❓ Troubleshooting

**MCP server not showing in Claude?**
- Check config file path: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Ensure JSON syntax is valid (use a JSON validator)
- Fully restart Claude Desktop (not just window close)
- Check Claude's logs: `~/Library/Logs/Claude/`

**Dependencies not found?**
- Ensure you're using the venv: `source .venv/bin/activate`
- Or reinstall: `uv pip install -r requirements.txt`

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
