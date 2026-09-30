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

- **server.py** - Main MCP server (FastMCP-style API: `MCPServer` + decorators)
- **requirements.txt** - Python dependencies (unpinned, always latest: `mcp[cli]`, `httpx`, `pytest`, `pytest-asyncio`)
- **memory.json** - Auto-created when you save memories
- **/prompts/** - Prompt template definitions
  - `weather_activity_planner.py` - Activity planning template (`render()` returns the prompt text)
  - `weather_alert_explainer.py` - Alert explanation template
- **/resources/** - Resource implementations
  - `memory_store.py` - Memory data resources
  - `server_status.py` - Server status resource
- **test_server.py** - Test suite for tools, resources, and prompts (`pytest.ini` enables async tests)

## 🚀 Setup & Running

### Installation (One-time)
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Run the Server Locally

**For Claude Desktop (stdio)**
```bash
source .venv/bin/activate
python server.py
```
Run manually it looks like it hangs — that's correct, it's waiting for stdin
from an MCP client. Normally Claude Desktop starts it for you (see the config below).

**For development & testing (MCP Inspector)**
```bash
source .venv/bin/activate
mcp dev server.py
```
Starts the [MCP Inspector](https://github.com/modelcontextprotocol/inspector). Open the
URL it prints (`http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=...`, the token is pre-filled),
click **Connect**, then use the **Tools**, **Resources** and **Prompts** tabs.

## 🔬 Testing with @modelcontextprotocol/inspector

The Inspector can also run without a browser (CLI mode), which is handy for scripts.
Launch it with `npx` and pass the command that starts your server — it spawns the server
itself, so you don't start `server.py` separately. Run these from the project root.

Shortcut used below:
```bash
INSPECT="npx -y @modelcontextprotocol/inspector --cli .venv/bin/python server.py"
```

**Web UI without `mcp dev`:**
```bash
npx @modelcontextprotocol/inspector .venv/bin/python server.py
```

**Tools**
```bash
$INSPECT --method tools/list
$INSPECT --method tools/call --tool-name get_time
$INSPECT --method tools/call --tool-name calculate --tool-arg a=25 b=4 operation=multiply
$INSPECT --method tools/call --tool-name save_memory --tool-arg key=project value="MCP Server"
$INSPECT --method tools/call --tool-name load_memory
$INSPECT --method tools/call --tool-name get_weather --tool-arg city=Bucharest
```
Example result for the `calculate` call:
```json
{
  "content": [{ "type": "text", "text": "25.0 multiply 4.0 = 100.0" }],
  "structuredContent": { "result": "25.0 multiply 4.0 = 100.0" },
  "isError": false
}
```
> Tool arguments use repeated `key=value` pairs after one `--tool-arg`. There is no
> JSON-argument flag: passing `--tool-args-json` silently sends **empty** arguments and
> the tool fails with "Field required".

**Resources**
```bash
$INSPECT --method resources/list
$INSPECT --method resources/read --uri memory://data
$INSPECT --method resources/read --uri status://server
```

**Prompts**
```bash
$INSPECT --method prompts/list
$INSPECT --method prompts/get --prompt-name weather_activity_planner \
  --prompt-args location=Colorado activity_type=hiking time_horizon="this weekend"
$INSPECT --method prompts/get --prompt-name weather_alert_explainer \
  --prompt-args alert_type="heat advisory" region=Texas
```

> In CLI mode the server command must come **first**, then the `--method ...` flags.

### Automated tests
```bash
source .venv/bin/activate
python -m pytest -q
```
The tests use a temporary memory file, so your real `memory.json` is never touched.

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

This server uses the high-level (FastMCP-style) API: you register plain Python functions
with decorators, and the name, description and argument schema come from the function
name, docstring and type hints. Restart the client (or `mcp dev`) after any change.

### Adding Tools
In `server.py`:
```python
@mcp.tool()
def shout(text: str) -> str:
    """Return the text in upper case."""
    return text.upper()
```
Use `async def` for anything that does network I/O, so the server isn't blocked.

### Adding Resources
Put the logic in `/resources/` (e.g. `my_resource.py` with a `read_...()` function), import it
in `/resources/__init__.py`, then register it in `server.py`:
```python
@mcp.resource("my://thing", name="My Thing", mime_type="text/plain")
def my_thing() -> str:
    """What this resource contains."""
    return my_resource.read_thing()
```

### Adding Prompts
Put the template in `/prompts/` (a `render(...) -> str` function), import it in
`/prompts/__init__.py`, then register it in `server.py`:
```python
@mcp.prompt()
def my_template(param1: str, param2: str = "default") -> str:
    """What this prompt does."""
    return my_template_module.render(param1, param2)
```
Parameters without a default are required; parameters with a default are optional.

> ⚠️ Don't give a registered function the same name as a module you import (e.g. a prompt
> function called `weather_activity_planner` next to `import weather_activity_planner`) —
> it shadows the module. `server.py` imports the prompt modules under aliases for this reason.

## ❓ Troubleshooting

**MCP server not showing in Claude?**
- Check config file path: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Ensure JSON syntax is valid (use a JSON validator)
- Fully restart Claude Desktop (not just window close)
- Check Claude's logs: `~/Library/Logs/Claude/`

**Dependencies not found?**
- Ensure you're using the venv: `source .venv/bin/activate`
- Or reinstall: `uv pip install -r requirements.txt`

**`mcp dev` says "PORT IS IN USE at port 6277"?**
- A previous Inspector is still running. Find it with `lsof -i :6277` and stop that
  process (`kill <PID>`), then run `mcp dev server.py` again.

**Tool call via the Inspector CLI fails with "Field required"?**
- Pass arguments as `--tool-arg key=value ...` (there is no `--tool-args-json`).

**Dependencies**
- `requirements.txt` is intentionally unpinned so installs always get the latest `mcp`
  and other libraries: `uv pip install -U -r requirements.txt`.

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
