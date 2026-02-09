# WHOOP MCP Server

Model Context Protocol server that exposes WHOOP fitness data to AI assistants.

## Features

This MCP server provides 8 tools to AI assistants:

| Tool | Description | Historical Data |
|------|-------------|----------------|
| `get_user_profile` | User profile information | No |
| `get_recovery_score` | Latest recovery score with HRV, RHR, sleep performance | Yes (days_ago) |
| `get_current_strain` | Current day strain score and heart rate | No |
| `get_recent_cycles` | Last 7 days of cycles with integrated recovery data | Yes (limit) |
| `get_latest_sleep` | Most recent sleep data with stages and quality | Yes (days_ago) |
| `get_recent_workouts` | Recent workout activities | Yes (limit) |
| `get_body_measurements` | Body measurements (height, weight, max HR) | No |
| `get_health_summary` | Comprehensive health snapshot (all data in one call) | No |

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

### Using Virtual Environment (Recommended)

For best compatibility with the project's dependencies:

```json
{
  "mcpServers": {
    "whoop-fitness": {
      "command": "C:\\path\\to\\agera-fastapi\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\agera-fastapi\\whoop_mcp_server.py"
      ]
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "whoop-fitness": {
      "command": "/path/to/agera-fastapi/.venv/bin/python",
      "args": [
        "/path/to/agera-fastapi/whoop_mcp_server.py"
      ]
    }
  }
}
```

## Usage Examples

Once configured in Claude Desktop, you can ask:

- "What's my recovery score today?"
- "Show me my last 7 days of data"
- "How did I sleep last night?"
- "What was my recovery 3 days ago?"
- "Show me my last 5 workouts"
- "How much strain do I have so far today?"
- "Give me a complete health summary"

## Architecture

```
┌─────────────────────┐
│   Claude Desktop    │
│   (MCP Client)      │
└──────────┬──────────┘
           │ stdio
           │
┌──────────▼──────────────┐
│  whoop_mcp_server.py    │
│  (MCP Server)           │
│  - 8 tools              │
│  - Token from cache     │
└──────────┬──────────────┘
           │ HTTPS + Bearer Token
           │
┌──────────▼──────────────┐
│   WHOOP API v2          │
│   api.prod.whoop.com    │
│   /developer/v2/        │
└─────────────────────────┘
           ▲
           │ OAuth 2.0
           │
┌──────────┴──────────────┐
│  whoop_simple.py        │
│  (FastAPI OAuth Server) │
│  - Initial auth         │
│  - Token caching        │
└─────────────────────────┘
```

## Token Management

- The MCP server reads from `.token_cache.json`
- Token is created by `whoop_simple.py` during OAuth
- If token expires, re-authenticate via FastAPI server
- No token refresh implemented (manual re-auth required)

## Limitations

- **Recovery/Sleep Data**: Only available for completed cycles (after sleep)
- **Real-time Data**: Strain updates in real-time, but recovery/sleep require cycle completion
- **Token Expiry**: No automatic refresh; re-authenticate via FastAPI server when token expires
- **Single User**: Only supports one authenticated user at a time
- **Historical Data**: Limited by WHOOP's data retention and API limits (typically last 30 days)
- **API Version**: Uses WHOOP API v2 (`/developer/v2/`)

## Troubleshooting

### "No access token found"
1. Start FastAPI server: `python whoop_simple.py`
2. Open browser to `http://localhost:3000`
3. Click "Click here to login with WHOOP" and complete OAuth
4. Verify `.token_cache.json` was created
5. Restart Claude Desktop

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

### API errors (404, 401, 403)
- **404 Not Found**: Ensure code uses `/developer/v2/` endpoints (not v1)
- **401 Unauthorized**: Token expired - re-authenticate via FastAPI server
- **403 Forbidden**: Check OAuth scopes in WHOOP Developer Console:
  - `read:profile`
  - `read:body_measurement`
  - `read:cycles`
  - `read:recovery`
  - `read:sleep`
  - `read:workout`
- Verify `.token_cache.json` exists and contains valid token
- Check WHOOP API status at [developer.whoop.com](https://developer.whoop.com/)

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

## Additional Documentation

See also:
- **[README.md](../README.md)** - Main project overview and quick start
- **[SETUP_MCP.md](SETUP_MCP.md)** - Step-by-step MCP setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast track setup
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design details

## Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [WHOOP API v2 Docs](https://developer.whoop.com/api)
- [WHOOP OpenAPI Spec](https://api.prod.whoop.com/developer/doc/openapi.json)
- [Claude Desktop](https://claude.ai/download)
- [Project Repository](https://github.com/shashwatchandra/whoop-fastapi-mcp)

## License

MIT
