# WHOOP MCP Server - Quick Setup Guide

## What You Created

You now have a **Model Context Protocol (MCP) server** that exposes your WHOOP fitness data to AI assistants like Claude Desktop!

## What is MCP?

MCP (Model Context Protocol) is a standard way for AI assistants to connect to data sources and tools. Think of it as a bridge that lets Claude (or other AI assistants) directly access your WHOOP data.

## Files Created

1. **whoop_mcp_server.py** - The MCP server with 8 tools
2. **MCP_README.md** - Full documentation
3. **claude_desktop_config.json** - Configuration template
4. **test_mcp_server.py** - Test script

## 3-Step Setup

### Step 1: Install MCP Python SDK

```bash
# Make sure your virtual environment is active
.venv\Scripts\activate

# Install MCP
pip install mcp
```

### Step 2: Test the Server

```bash
# Run the MCP server directly
python whoop_mcp_server.py
```

You should see:
```
🏃 Starting WHOOP MCP Server...
📊 Available tools:
  - get_user_profile: Get user profile information
  - get_recovery_score: Get latest recovery score
  ...
⚡ Server running on stdio transport...
```

Press Ctrl+C to stop.

### Step 3: Add to Claude Desktop

1. **Find your Claude Desktop config file:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Add this configuration** (update the path):

```json
{
  "mcpServers": {
    "whoop-fitness": {
      "command": "python",
      "args": [
        "c:\\Shash\\Agera\\agera-fastapi\\whoop_mcp_server.py"
      ]
    }
  }
}
```

3. **Restart Claude Desktop completely** (quit and reopen)

4. **Test in Claude Desktop:**
   - Open Claude Desktop
   - Look for a 🔌 icon or "Tools" indicator
   - Ask: "What's my recovery score today?"

## Available Tools

Once connected, you can ask Claude:

| Tool | Example Question |
|------|------------------|
| `get_user_profile` | "Show my WHOOP profile" |
| `get_recovery_score` | "What's my recovery today?" |
| `get_current_strain` | "How much strain do I have?" |
| `get_recent_cycles` | "Show my last 7 days" |
| `get_latest_sleep` | "How did I sleep last night?" |
| `get_recent_workouts` | "Show my last 5 workouts" |
| `get_body_measurements` | "What are my body metrics?" |
| `get_health_summary` | "Give me my health overview" |

## Important Notes

### Token Requirement
The MCP server reads from `.token_cache.json` which is created when you authenticate via the FastAPI server:

```bash
# If you haven't authenticated yet:
python whoop_simple.py
# Then visit http://localhost:3000/login
```

### Data Availability
- **Strain**: Updates in real-time ✅
- **Recovery**: Available after sleep completion 💤
- **Sleep**: Available after cycle ends 🌙

## Troubleshooting

### Claude Desktop doesn't see the server
1. Check config file path is correct
2. Verify Python path in config
3. **Completely restart Claude Desktop** (not just refresh)
4. Check Claude logs (Help → Debug Info)

### "No access token found"
Run `python whoop_simple.py` and authenticate at `/login` first.

### Import errors
```bash
pip install mcp
pip install httpx python-dotenv
```

## Test Without Claude Desktop

Use the test script:

```bash
python test_mcp_server.py
```

This simulates an MCP client connecting to your server.

## What's Next?

Once everything works:

1. **Use with Claude Desktop** - Ask questions naturally about your health
2. **Customize Tools** - Add more WHOOP endpoints in `whoop_mcp_server.py`
3. **Add AI Insights** - Connect to Ollama through the MCP server
4. **Share with Team** - Others can connect to your MCP server

## Architecture

```
Claude Desktop (AI Assistant)
        ↓
    MCP Protocol (stdio)
        ↓
whoop_mcp_server.py (Your Server)
        ↓
    WHOOP API (developer/v1)
        ↓
    Your Health Data
```

## Need Help?

- See [MCP_README.md](MCP_README.md) for full documentation
- Visit [modelcontextprotocol.io](https://modelcontextprotocol.io/) for MCP docs
- Check [WHOOP API docs](https://developer.whoop.com/)

---

**You're all set! 🎉**

Try asking Claude: *"What's my recovery score and should I train hard today?"*
