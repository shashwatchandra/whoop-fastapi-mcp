# WHOOP FastAPI + MCP Server

Full-stack WHOOP integration with FastAPI OAuth server and Model Context Protocol (MCP) server for Claude Desktop.

## 🚀 Features

- **FastAPI OAuth Server** - Authenticate with WHOOP and access your health data
- **MCP Server** - Integrate WHOOP data directly into Claude Desktop conversations
- **Complete Data Access** - Recovery, sleep, workouts, cycles, and body measurements
- **Historical Queries** - Access data from specific dates or date ranges
- **Secure** - OAuth 2.0 authentication with encrypted token storage

## 📦 What's Included

### 1. FastAPI Application (`whoop_simple.py`)
Web server for WHOOP OAuth authentication and data exploration:
- OAuth 2.0 flow with WHOOP API
- Dashboard with health metrics
- REST API endpoints for all WHOOP data
- Token caching for seamless access

### 2. MCP Server (`whoop_mcp_server.py`)
Model Context Protocol server for Claude Desktop integration:
- 8 tools for accessing WHOOP data
- Support for historical data queries
- Recovery scores, sleep analysis, workout tracking
- Cycles and strain monitoring

## Prerequisites
- Python 3.10+
- VS Code with Python extension (optional)
- HTTPS dev URL (ngrok/cloudflared) for OAuth redirect
- Claude Desktop (for MCP integration)
- WHOOP Developer App credentials from [developer.whoop.com](https://developer.whoop.com/)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
WHOOP_CLIENT_ID=your_client_id_here
WHOOP_CLIENT_SECRET=your_client_secret_here
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok-free.dev
```

### 3. Setup OAuth Tunnel

```bash
# Start ngrok
ngrok http 3000
```

Copy the HTTPS URL and:
1. Update `PUBLIC_BASE_URL` in `.env`
2. Set callback URL in [WHOOP Developer Console](https://developer.whoop.com/) to:
   ```
   https://your-ngrok-url.ngrok-free.dev/callback
   ```

### 4. Authenticate with WHOOP

```bash
# Start FastAPI server
python whoop_simple.py

# Open browser to http://localhost:3000
# Click "Click here to login with WHOOP"
# Complete OAuth authorization
```

Once authenticated, a `.token_cache.json` file is created with your OAuth token.

### 5. Try FastAPI Endpoints

- `http://localhost:3000/dashboard` - Health dashboard
- `http://localhost:3000/me` - Profile + body measurements
- `http://localhost:3000/daily?day=YYYY-MM-DD` - Daily cycles

### 6. Setup MCP Server (Optional)

For Claude Desktop integration:

1. **Configure Claude Desktop:**

   Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

   ```json
   {
     "mcpServers": {
       "whoop-fitness": {
         "command": "C:\\path\\to\\.venv\\Scripts\\python.exe",
         "args": ["C:\\path\\to\\whoop_mcp_server.py"]
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Test in Claude:**
   - "What's my recovery score today?"
   - "Show me my last 7 days of data"
   - "How did I sleep last night?"

See [docs/SETUP_MCP.md](docs/SETUP_MCP.md) for detailed MCP setup instructions.

## 📖 Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Fast setup and running guide
- **[SETUP_MCP.md](docs/SETUP_MCP.md)** - Complete MCP server setup for Claude Desktop
- **[MCP_README.md](docs/MCP_README.md)** - MCP server documentation and available tools
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design
- **[SECURITY_CHECKLIST.md](docs/SECURITY_CHECKLIST.md)** - Security guidelines for GitHub

## 🔧 Available MCP Tools

Once configured with Claude Desktop, you can use these tools:

| Tool | Description |
|------|-------------|
| `get_user_profile` | Get user profile and basic info |
| `get_recovery_score` | Latest recovery score with HRV, RHR |
| `get_current_strain` | Current day strain and heart rate |
| `get_recent_cycles` | Last 7 days of cycles with recovery |
| `get_latest_sleep` | Most recent sleep data and stages |
| `get_recent_workouts` | Recent workout activities |
| `get_body_measurements` | Height, weight, max heart rate |
| `get_health_summary` | Complete health overview |

## 🔐 Security

All sensitive data is protected:
- `.env` - API credentials (in .gitignore)
- `.token_cache.json` - OAuth tokens (in .gitignore)
- `.venv/` - Virtual environment (in .gitignore)

Safe to commit and share on GitHub!

## 🐛 Troubleshooting

### FastAPI Issues
- **404 errors**: Ensure using `/developer/v2/` API base
- **OAuth callback fails**: Verify ngrok is running and URLs match
- **No data returned**: Check scopes in WHOOP Developer Console include:
  - `read:profile`
  - `read:body_measurement`
  - `read:cycles`
  - `read:recovery`
  - `read:sleep`
  - `read:workout`

### MCP Server Issues
- **Claude Desktop doesn't see server**: Check config file path and restart Claude Desktop
- **"No access token found"**: Authenticate via FastAPI server first (`http://localhost:3000/login`)
- **Tools not appearing**: Verify Python path in config points to virtual environment

## 📝 API Endpoints

### FastAPI Server Endpoints
- `GET /` - Home page with links
- `GET /login` - Start OAuth flow
- `GET /callback` - OAuth callback handler
- `GET /me` - User profile and measurements
- `GET /daily?day=YYYY-MM-DD` - Cycles for specific day
- `GET /dashboard` - Health dashboard with recent data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- WHOOP API for health data access
- Model Context Protocol (MCP) for AI integration
- FastAPI for the web framework
- Claude Desktop for MCP support
