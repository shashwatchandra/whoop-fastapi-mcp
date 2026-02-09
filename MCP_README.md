# WHOOP MCP Server

Model Context Protocol server that exposes WHOOP fitness data to AI assistants.

## Features

This MCP server provides the following tools to AI assistants:

- **get_user_profile**: Fetch user profile information
- **get_recovery_score**: Get latest recovery score (HRV, RHR, sleep performance)
- **get_current_strain**: Get current day strain score
- **get_recent_cycles**: Get recent physiological cycles (24-hour periods)
- **get_latest_sleep**: Get most recent sleep data with stages and quality
- **get_recent_workouts**: Get recent workout activities
- **get_body_measurements**: Get body measurements (height, weight, max HR)
- **get_health_summary**: Get comprehensive health snapshot (all data in one call)

## Prerequisites

1. **Python Environment**: Python 3.10+ with required packages
2. **WHOOP OAuth Token**: Authenticated token cached from the FastAPI server
3. **MCP Client**: Claude Desktop or another MCP-compatible client

## Installation

### 1. Install MCP SDK

```bash
# Using pip
pip install mcp

# Or using uv (recommended)
uv pip install mcp
```

### 2. Authenticate with WHOOP

First, run the FastAPI server to authenticate and cache your token:

```bash
python whoop_simple.py
```

Visit `http://localhost:3000/login` and complete OAuth flow. This creates `.token_cache.json`.

### 3. Test the MCP Server

```bash
# Run directly
python whoop_mcp_server.py

# Or with uv
uv run whoop_mcp_server.py
```

## Configuration

### Claude Desktop Setup

Add this configuration to your Claude Desktop config file:

**Location:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Config:**
```json
{
  "mcpServers": {
    "whoop-fitness": {
      "command": "python",
      "args": [
        "C:\\path\\to\\agera-fastapi\\whoop_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\agera-fastapi"
      }
    }
  }
}
```

Replace `C:\\path\\to\\agera-fastapi` with your actual path.

### Using with uv

For better isolation, use `uv`:

```json
{
  "mcpServers": {
    "whoop-fitness": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "python",
        "C:\\path\\to\\agera-fastapi\\whoop_mcp_server.py"
      ]
    }
  }
}
```

## Usage Examples

Once configured in Claude Desktop, you can ask:

- "What's my recovery score today?"
- "Show me my last 5 workouts"
- "How much strain do I have so far today?"
- "What was my sleep quality last night?"
- "Give me a health summary"

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
│   (MCP Client)  │
└────────┬────────┘
         │ stdio
         │
┌────────▼────────────┐
│  whoop_mcp_server   │
│  (MCP Server)       │
└────────┬────────────┘
         │ HTTP
         │
┌────────▼────────────┐
│   WHOOP API         │
│   (developer/v1)    │
└─────────────────────┘
```

## Token Management

- The MCP server reads from `.token_cache.json`
- Token is created by `whoop_simple.py` during OAuth
- If token expires, re-authenticate via FastAPI server
- No token refresh implemented (manual re-auth required)

## Limitations

- **Recovery/Sleep Data**: Only available for completed cycles (after sleep)
- **Real-time Data**: Strain updates in real-time, but recovery/sleep require cycle completion
- **Token Expiry**: No automatic refresh; re-authenticate when token expires
- **Single User**: Only supports one authenticated user at a time

## Troubleshooting

### "No access token found"
Run `python whoop_simple.py` and authenticate at `/login` endpoint first.

### Claude Desktop doesn't see tools
1. Check config file location and syntax
2. Verify Python path is correct
3. Restart Claude Desktop completely
4. Check Claude logs for errors

### Import errors
```bash
# Install mcp package
pip install mcp

# Or with all dependencies
pip install -r requirements.txt
```

### API errors
- Verify `.token_cache.json` exists and contains valid token
- Check WHOOP API status
- Ensure all OAuth scopes were granted

## Development

### Adding New Tools

```python
@mcp.tool()
async def your_new_tool(param: str) -> dict[str, Any]:
    """Tool description for AI."""
    return await make_api_request(f"/your/endpoint")
```

### Testing

```bash
# Run server in debug mode
python whoop_mcp_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python whoop_mcp_server.py
```

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [WHOOP API Docs](https://developer.whoop.com/)
- [Claude Desktop](https://claude.ai/download)

## License

MIT
