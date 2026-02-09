# Quick Start Guide

## ✅ Your Current Setup (Already Done)

You have:
- ✅ `.env` file with real WHOOP credentials
- ✅ `.token_cache.json` with valid OAuth token
- ✅ Virtual environment configured
- ✅ All dependencies installed

**Everything will continue to work as-is!**

## 🚀 Running Your Applications

### 1. MCP Server (for Claude Desktop)
Your MCP server starts automatically when Claude Desktop launches.
- Config: `%APPDATA%\Claude\claude_desktop_config.json`
- Status: Already configured ✅

### 2. FastAPI Server (for OAuth)
```powershell
.\.venv\Scripts\python.exe whoop_simple.py
```
Then visit: http://localhost:3000

### 3. Test MCP Server Manually
```powershell
.\.venv\Scripts\python.exe whoop_mcp_server.py
```

## 📦 After Cloning (For Others)

When someone clones your repo, they need to:

1. **Copy environment template:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` and add their WHOOP credentials:**
   ```
   WHOOP_CLIENT_ID=their_client_id
   WHOOP_CLIENT_SECRET=their_client_secret
   ```

3. **Create virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Authenticate with WHOOP:**
   ```powershell
   python whoop_simple.py
   # Visit http://localhost:3000/login
   ```

6. **Configure Claude Desktop** (if using MCP):
   - Edit `%APPDATA%\Claude\claude_desktop_config.json`
   - Add the whoop-fitness server config
   - Restart Claude Desktop

## 🔍 Verify Everything Works

```powershell
# Test environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('CLIENT_ID:', os.getenv('WHOOP_CLIENT_ID')[:10])"

# Test token exists
Test-Path .token_cache.json

# Test MCP import
python -c "from mcp.server import Server; print('MCP OK')"
```

## ⚠️ Important Notes

- `.env` is **NOT** in git (protected by .gitignore)
- `.token_cache.json` is **NOT** in git
- Each user needs their own WHOOP Developer App credentials
- Get credentials at: https://developer.whoop.com/
