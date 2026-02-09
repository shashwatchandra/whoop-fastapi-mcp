# WHOOP MCP Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interactions                         │
└────────────┬────────────────────────────────┬───────────────┘
             │                                 │
             │ Natural Language                │ HTTP Requests
             │ Questions                       │
             │                                 │
┌────────────▼──────────────┐    ┌───────────▼──────────────┐
│   Claude Desktop App      │    │   Web Browser            │
│   (MCP Client)            │    │                          │
│   • AI Assistant          │    │   • Dashboard UI         │
│   • Tool Calling          │    │   • Manual Data Access   │
└────────────┬──────────────┘    └───────────┬──────────────┘
             │                                 │
             │ stdio (MCP Protocol)           │ HTTP (REST)
             │                                 │
┌────────────▼──────────────┐    ┌───────────▼──────────────┐
│  whoop_mcp_server.py      │    │   whoop_simple.py        │
│  (MCP Server)             │    │   (FastAPI Server)       │
│                           │    │                          │
│  Tools:                   │    │  Endpoints:              │
│  • get_user_profile       │    │  • /login                │
│  • get_recovery_score     │    │  • /callback             │
│  • get_current_strain     │    │  • /dashboard            │
│  • get_recent_cycles      │    │  • /cycles-view          │
│  • get_latest_sleep       │    │  • /workouts-view        │
│  • get_recent_workouts    │    │  • /sleep-view           │
│  • get_body_measurements  │    │  • /recovery-view        │
│  • get_health_summary     │    │  • /ai-insights-view     │
└────────────┬──────────────┘    └───────────┬──────────────┘
             │                                 │
             │ Reads Token                    │ Saves Token
             │                                 │
             └──────────┬───────────┬─────────┘
                        │           │
                   ┌────▼───────────▼────┐
                   │  .token_cache.json  │
                   │  (OAuth Token)      │
                   └─────────────────────┘
                              │
                              │ Bearer Token
                              │
                    ┌─────────▼──────────┐
                    │   WHOOP API        │
                    │   (REST API)       │
                    │                    │
                    │  Base URL:         │
                    │  api.prod.whoop.com│
                    │  /developer/v1     │
                    │                    │
                    │  Endpoints:        │
                    │  • /user/profile   │
                    │  • /cycle          │
                    │  • /cycle/{id}/    │
                    │    recovery        │
                    │  • /cycle/{id}/    │
                    │    sleep           │
                    │  • /activity/      │
                    │    workout         │
                    └────────────────────┘
```

## Data Flow

### 1. Initial Authentication (One-Time Setup)
```
User → Browser → whoop_simple.py (/login)
                      ↓
                 WHOOP OAuth
                      ↓
             /callback endpoint
                      ↓
            Save to .token_cache.json
```

### 2. MCP Tool Call (AI Assistant)
```
User: "What's my recovery?"
        ↓
Claude Desktop (MCP Client)
        ↓ (stdio)
whoop_mcp_server.py
        ↓ (reads token)
.token_cache.json
        ↓ (HTTP + Bearer token)
WHOOP API
        ↓
Response data
        ↓
whoop_mcp_server.py (formats)
        ↓ (stdio)
Claude Desktop
        ↓
User: "Your recovery is 85%"
```

### 3. Web Dashboard Access
```
User → Browser → whoop_simple.py (/dashboard)
                      ↓ (reads token)
               .token_cache.json
                      ↓ (HTTP + Bearer token)
                 WHOOP API
                      ↓
               Format as HTML
                      ↓
                 Browser Display
```

## File Structure

```
agera-fastapi/
├── whoop_simple.py              # FastAPI server (OAuth + Web UI)
├── whoop_mcp_server.py          # MCP server (AI assistant interface)
├── test_mcp_server.py           # MCP testing script
│
├── .env                         # Environment variables
├── .token_cache.json            # Cached OAuth token (created after login)
│
├── requirements.txt             # FastAPI dependencies
├── requirements_mcp.txt         # MCP-specific dependencies
│
├── README.md                    # FastAPI server docs
├── MCP_README.md                # MCP server full docs
├── SETUP_MCP.md                 # MCP quick setup guide
├── ARCHITECTURE.md              # This file
└── claude_desktop_config.json   # MCP client configuration template
```

## Component Details

### whoop_simple.py (FastAPI Server)
**Purpose**: Web-based access to WHOOP data with OAuth authentication  
**Port**: 3000  
**Transport**: HTTP/HTTPS  
**Auth**: OAuth 2.0 Authorization Code Flow  
**Features**:
- OAuth login flow
- Token caching
- HTML dashboard
- AI insights (Ollama)
- Manual data browsing

### whoop_mcp_server.py (MCP Server)
**Purpose**: AI assistant interface to WHOOP data  
**Port**: N/A (stdio)  
**Transport**: stdio (standard input/output)  
**Auth**: Uses cached token from FastAPI server  
**Features**:
- 8 MCP tools
- Async API calls
- Error handling
- Token reuse

### .token_cache.json (Shared Token)
**Purpose**: Persistent OAuth token storage  
**Format**: JSON  
**Contents**:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read:profile read:cycles ...",
  "refresh_token": "..."
}
```

## Network Topology

```
Internet
    │
    ├─── WHOOP API (api.prod.whoop.com)
    │         ↑
    │         │ HTTPS + Bearer Token
    │         │
    ├─────────┼─── whoop_simple.py (localhost:3000)
    │         │          ↑
    │         │          │ HTTP
    │         │          │
    │         │     Web Browser
    │         │
    │         └─── .token_cache.json
    │                     ↑
    │                     │ File I/O (read)
    │                     │
    └───────────────── whoop_mcp_server.py
                              ↑
                              │ stdio (MCP Protocol)
                              │
                        Claude Desktop
                              ↑
                              │
                           User
```

## Protocol Stack

### FastAPI Server Stack
```
Layer 7: HTML/CSS (UI)
Layer 6: FastAPI Routes
Layer 5: Python Logic (OAuth, API calls)
Layer 4: HTTP/HTTPS
Layer 3: TCP/IP
```

### MCP Server Stack
```
Layer 7: MCP Tools (JSON-RPC)
Layer 6: MCP Protocol (stdio)
Layer 5: Python Logic (API calls)
Layer 4: HTTP/HTTPS (to WHOOP API)
Layer 3: TCP/IP
```

## Security Considerations

### Token Storage
- ✅ Local file (.token_cache.json)
- ✅ Not committed to git (.gitignore)
- ⚠️ No encryption at rest
- ⚠️ Shared between two processes

### Network Security
- ✅ HTTPS to WHOOP API
- ✅ OAuth 2.0 with scopes
- ✅ Bearer token authentication
- ⚠️ No token refresh implemented
- ⚠️ Token expiry not monitored

### MCP Security
- ✅ Local stdio only (no network exposure)
- ✅ Tools require valid token
- ✅ Read-only operations
- ⚠️ No user authentication on MCP

## Scalability Notes

### Current Limitations
- Single user (one token)
- No concurrent request handling in MCP
- No rate limiting
- No caching beyond token

### Potential Improvements
1. **Multi-user**: Database for multiple tokens
2. **Caching**: Redis for API response caching
3. **Rate Limiting**: Respect WHOOP API limits
4. **Token Refresh**: Automatic renewal
5. **MCP Authentication**: User verification
6. **Monitoring**: Logging and metrics

## Deployment Options

### Current (Local Development)
```
Laptop
├── Python 3.13
├── FastAPI (port 3000)
├── MCP Server (stdio)
└── Claude Desktop
```

### Production Option 1 (Cloud FastAPI)
```
Cloud VM
├── FastAPI (HTTPS)
├── PostgreSQL (token storage)
└── Reverse proxy (nginx)

Local Machine
├── Claude Desktop
└── MCP Server → Cloud API
```

### Production Option 2 (Serverless)
```
AWS Lambda / Azure Functions
├── FastAPI endpoints
└── DynamoDB (token storage)

Local Machine
├── Claude Desktop
└── MCP Server → Serverless API
```

## Use Cases

### Use Case 1: Morning Health Check
```
User → Claude: "Should I work out today?"
         ↓
Claude → MCP Server: get_health_summary()
         ↓
MCP Server → WHOOP API: GET /cycle, /recovery
         ↓
MCP Server → Claude: {recovery: 85%, strain: 4.2, ...}
         ↓
Claude → User: "Your recovery is excellent at 85%! 
                Your body is ready for a challenging workout."
```

### Use Case 2: Weekly Review
```
User → Browser: http://localhost:3000/cycles-view
         ↓
FastAPI → WHOOP API: GET /cycle?limit=7
         ↓
FastAPI → Browser: HTML table with 7 days of data
         ↓
User sees: Strain, Recovery, Sleep for past week
```

### Use Case 3: Workout Analysis
```
User → Claude: "Compare my last 3 workouts"
         ↓
Claude → MCP Server: get_recent_workouts(limit=3)
         ↓
MCP Server → WHOOP API: GET /activity/workout?limit=3
         ↓
MCP Server → Claude: [{strain: 15.2, hr_avg: 145}, ...]
         ↓
Claude → User: "Your workouts show increasing intensity:
                Workout 1: 12.5 strain, 140 avg HR
                Workout 2: 14.1 strain, 143 avg HR
                Workout 3: 15.2 strain, 145 avg HR"
```

## Integration Points

### Current Integrations
- ✅ WHOOP API (developer/v1)
- ✅ Ollama (AI insights)
- ✅ Claude Desktop (MCP)

### Future Integration Ideas
- 📋 Google Sheets (export data)
- 📋 Notion (workout journal)
- 📋 Strava (sync workouts)
- 📋 Apple Health (import data)
- 📋 Slack (daily recovery bot)
- 📋 Discord (fitness community)

## Development Workflow

```
1. Code Change
   ↓
2. Test FastAPI Server
   python whoop_simple.py
   ↓
3. Test MCP Server
   python test_mcp_server.py
   ↓
4. Test in Claude Desktop
   Ask questions
   ↓
5. Deploy
   Commit to git
```

## Monitoring & Debugging

### Logs
- FastAPI: Console output (uvicorn)
- MCP Server: Console output (stdio)
- Claude Desktop: Help → Debug Info

### Testing Tools
- HTTP: curl, Postman
- MCP: test_mcp_server.py, MCP Inspector
- API: WHOOP Developer Console

---

**Last Updated**: Feb 8, 2026  
**Version**: 1.0  
**Status**: Development
