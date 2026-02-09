"""
WHOOP OAuth - Dead Simple Version
Run this and follow the instructions
"""
import os
import sys
import json
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
import uvicorn
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - Use environment variables
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET", "")
NGROK_URL = os.getenv("PUBLIC_BASE_URL", "https://hyponastically-electronegative-angelita.ngrok-free.dev")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TOKEN_CACHE_FILE = ".token_cache.json"

# Validate required credentials
if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ ERROR: WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET must be set in .env file")
    sys.exit(1)

# Initialize AI client (Ollama or OpenAI)
if USE_OLLAMA or not OPENAI_API_KEY:
    # Use Ollama (free local model)
    ai_client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama"  # Ollama doesn't need a real API key
    )
    ai_model = OLLAMA_MODEL
    print(f"🤖 Using Ollama with model: {ai_model}")
elif OPENAI_API_KEY:
    # Use OpenAI
    ai_client = OpenAI(api_key=OPENAI_API_KEY)
    ai_model = "gpt-4o-mini"
    print("🤖 Using OpenAI")
else:
    ai_client = None
    ai_model = None
    print("⚠️ No AI client configured")

app = FastAPI()

# Simple in-memory storage
tokens = {}
state_store = "test12345"  # Fixed state (must be 8+ chars for WHOOP)

def save_token(access_token):
    """Save token to cache file"""
    try:
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump({"access_token": access_token}, f)
        print("💾 Token cached to file")
    except Exception as e:
        print(f"❌ Error saving token: {e}")

def load_token():
    """Load token from cache file"""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                if "access_token" in data:
                    tokens["access_token"] = data["access_token"]
                    print("✅ Loaded cached token")
                    return True
    except Exception as e:
        print(f"❌ Error loading token: {e}")
    return False

# Load cached token on startup
load_token()

@app.get("/")
def home():
    logged_in = "access_token" in tokens
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WHOOP Dashboard</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
            }}
            .nav {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }}
            .nav-item {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-decoration: none;
                text-align: center;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .nav-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }}
            .nav-item.ai {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .status {{
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
            }}
            .login-btn {{
                background: #4caf50;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                font-weight: 600;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏃 WHOOP Dashboard</h1>
            <p class="subtitle">Your personal health and fitness insights powered by AI</p>
            
            {'<div class="status">✅ <strong>Logged in!</strong> Explore your data below.</div>' if logged_in else '<p>Please <a href="/login" class="login-btn">Login with WHOOP</a> to access your data.</p>'}
            
            {f'''<div class="nav">
                <a href="/dashboard" class="nav-item">📊 Dashboard</a>
                <a href="/cycles-view" class="nav-item">🔄 Cycles</a>
                <a href="/workouts-view" class="nav-item">💪 Workouts</a>
                <a href="/sleep-view" class="nav-item">😴 Sleep</a>
                <a href="/recovery-view" class="nav-item">❤️ Recovery</a>
                <a href="/ai-insights-view" class="nav-item ai">🤖 AI Insights</a>
            </div>''' if logged_in else ''}
            
            <div style="margin-top: 30px; padding: 15px; background: #f5f5f5; border-radius: 8px; font-size: 0.9em; color: #666;">
                <strong>Setup:</strong>
                <ul style="margin: 10px 0;">
                    <li>ngrok running: <code>ngrok http 3000</code></li>
                    <li>Callback URL: <code>{NGROK_URL}/callback</code></li>
    </ul>
    """)

@app.get("/test")
def test():
    """Test if server is reachable"""
    return {"status": "Server is working!", "ngrok_url": NGROK_URL}

@app.get("/login")
def login():
    print("\n🔵 LOGIN ENDPOINT HIT!")
    auth_url = (
        f"https://api.prod.whoop.com/oauth/oauth2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={NGROK_URL}/callback&"
        f"response_type=code&"
        f"scope=read:profile read:body_measurement read:cycles read:recovery read:workout read:sleep&"
        f"state={state_store}"
    )
    print(f"Redirecting to WHOOP...")
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    print("\n🟢 CALLBACK ENDPOINT HIT!")
    print(f"Query params: {dict(request.query_params)}")
    
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    if state != state_store:
        return {"error": "Invalid state"}
    
    if not code:
        return {"error": "No code received"}
    
    print(f"Got code: {code[:20]}...")
    print("Exchanging for token...")
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.prod.whoop.com/oauth/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{NGROK_URL}/callback",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
        
        print(f"Token response: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            tokens["access_token"] = token_data["access_token"]
            save_token(token_data["access_token"])
            print("✅ SUCCESS! Got access token!")
            return RedirectResponse("/dashboard")
        else:
            print(f"❌ ERROR: {response.text}")
            return {"error": "Token exchange failed", "details": response.text}

@app.get("/profile")
async def profile():
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    print("\n📊 Fetching WHOOP data...")
    
    async with httpx.AsyncClient() as client:
        # Use the correct developer API base URL
        profile_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/user/profile/basic",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        body_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/user/body_measurement",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        cycles_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
    
    print(f"✅ Profile: {profile_response.status_code}")
    print(f"✅ Body: {body_response.status_code}")
    print(f"✅ Cycles: {cycles_response.status_code}")
    
    return {
        "profile": profile_response.json() if profile_response.status_code == 200 else None,
        "body_measurement": body_response.json() if body_response.status_code == 200 else None,
        "cycles": cycles_response.json() if cycles_response.status_code == 200 else None,
    }

@app.get("/cycles")
async def get_cycles(start: str = None, end: str = None):
    """Get cycle data with optional date range (YYYY-MM-DD format)"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    print(f"\n📊 Fetching cycles data (start={start}, end={end})...")
    
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params=params
        )
    
    print(f"✅ Cycles: {response.status_code}")
    return response.json() if response.status_code == 200 else {"error": response.text}

@app.get("/workouts")
async def get_workouts(start: str = None, end: str = None):
    """Get workout data with optional date range (YYYY-MM-DD format)"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    print(f"\n🏃 Fetching workouts data (start={start}, end={end})...")
    
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/workout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params=params
        )
    
    print(f"✅ Workouts: {response.status_code}")
    return response.json() if response.status_code == 200 else {"error": response.text}

@app.get("/sleep")
async def get_sleep(start: str = None, end: str = None):
    """Get sleep data with optional date range (YYYY-MM-DD format)"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    print(f"\n😴 Fetching sleep data (start={start}, end={end})...")
    
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/activity/sleep",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params=params
        )
    
    print(f"✅ Sleep: {response.status_code}")
    return response.json() if response.status_code == 200 else {"error": response.text}

@app.get("/recovery")
async def get_current_recovery():
    """Get current recovery score for the latest cycle"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    print("\n💪 Fetching current recovery...")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get the latest cycle (limit=1)
        cycle_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "1"}
        )
        
        print(f"✅ Latest Cycle: {cycle_response.status_code}")
        
        if cycle_response.status_code != 200:
            return {"error": "Could not fetch cycle", "details": cycle_response.text}
        
        cycle_data = cycle_response.json()
        
        if not cycle_data.get("records") or len(cycle_data["records"]) == 0:
            return {"message": "No cycles found yet"}
        
        latest_cycle = cycle_data["records"][0]
        cycle_id = latest_cycle["id"]
        
        print(f"📋 Cycle ID: {cycle_id}")
        
        # Step 2: Get recovery for this cycle
        recovery_response = await client.get(
            f"https://api.prod.whoop.com/developer/v1/cycle/{cycle_id}/recovery",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        print(f"✅ Recovery: {recovery_response.status_code}")
        
        if recovery_response.status_code == 200:
            recovery_data = recovery_response.json()
            return {
                "cycle": latest_cycle,
                "recovery": recovery_data
            }
        elif recovery_response.status_code == 404:
            return {
                "cycle": latest_cycle,
                "recovery": None,
                "message": "No recovery data for this cycle yet"
            }
        else:
            return {"error": "Could not fetch recovery", "details": recovery_response.text}

@app.get("/dashboard")
async def dashboard():
    """Main dashboard with overview of all data"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    async with httpx.AsyncClient() as client:
        profile_resp = await client.get(
            "https://api.prod.whoop.com/developer/v1/user/profile/basic",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        cycles_resp = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "1"}
        )
    
    profile = profile_resp.json() if profile_resp.status_code == 200 else {}
    cycles = cycles_resp.json() if cycles_resp.status_code == 200 else {"records": []}
    latest_cycle = cycles.get("records", [])[0] if cycles.get("records") else None
    
    print(f"\n📊 Dashboard - Latest Cycle Data: {latest_cycle}")
    
    recovery_score = None
    strain_score = None
    sleep_performance = None
    
    if latest_cycle:
        # Strain is in the cycle's score
        score = latest_cycle.get("score", {})
        strain_score = score.get("strain")
        
        cycle_id = latest_cycle.get("id")
        
        # Fetch recovery and sleep data separately
        if cycle_id:
            async with httpx.AsyncClient() as client:
                # Fetch recovery
                recovery_resp = await client.get(
                    f"https://api.prod.whoop.com/developer/v1/cycle/{cycle_id}/recovery",
                    headers={"Authorization": f"Bearer {tokens['access_token']}"}
                )
                if recovery_resp.status_code == 200:
                    recovery_data = recovery_resp.json()
                    recovery_score = recovery_data.get("score", {}).get("recovery_score")
                    print(f"✅ Recovery: {recovery_score}")
                else:
                    print(f"⚠️ Recovery: {recovery_resp.status_code} - {recovery_resp.text[:100]}")
                
                # Fetch sleep
                sleep_resp = await client.get(
                    f"https://api.prod.whoop.com/developer/v1/cycle/{cycle_id}/sleep",
                    headers={"Authorization": f"Bearer {tokens['access_token']}"}
                )
                if sleep_resp.status_code == 200:
                    sleep_data = sleep_resp.json()
                    sleep_performance = sleep_data.get("score", {}).get("sleep_performance_percentage")
                    print(f"✅ Sleep: {sleep_performance}%")
                else:
                    print(f"⚠️ Sleep: {sleep_resp.status_code} - {sleep_resp.text[:100]}")
        
        print(f"Dashboard metrics - Recovery: {recovery_score}, Strain: {strain_score}, Sleep: {sleep_performance}")
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .metric-label {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 8px;
            }}
            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #333;
            }}
            .metric-icon {{
                font-size: 2em;
                margin-bottom: 10px;
            }}
            .recovery-green {{ color: #4caf50; }}
            .recovery-yellow {{ color: #ff9800; }}
            .recovery-red {{ color: #f44336; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
                transition: background 0.2s;
            }}
            .nav-bar a:hover {{
                background: #f0f0f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/cycles-view">🔄 Cycles</a>
                <a href="/ai-insights-view">🤖 AI Insights</a>
            </div>
            
            <div class="header">
                <h1>👋 Welcome, {profile.get('first_name', 'User')}!</h1>
                <p>Here's your health overview</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-icon">❤️</div>
                    <div class="metric-label">Recovery</div>
                    <div class="metric-value {'recovery-green' if recovery_score and recovery_score >= 67 else 'recovery-yellow' if recovery_score and recovery_score >= 34 else 'recovery-red'}">
                        {f'{recovery_score}%' if recovery_score else 'N/A'}
                    </div>
                    {'' if recovery_score else '<div style="font-size: 0.7em; color: #999; margin-top: 10px;">Available after sleep</div>'}
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">💪</div>
                    <div class="metric-label">Strain</div>
                    <div class="metric-value">
                        {f'{strain_score:.1f}' if strain_score else 'N/A'}
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">😴</div>
                    <div class="metric-label">Sleep Performance</div>
                    <div class="metric-value">
                        {f'{sleep_performance}%' if sleep_performance else 'N/A'}
                    </div>
                    {'' if sleep_performance else '<div style="font-size: 0.7em; color: #999; margin-top: 10px;">Available after sleep</div>'}
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/ai-insights-view")
async def ai_insights_view():
    """HTML view for AI insights"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    # Get the insights from the API
    insights_data = await ai_insights()
    
    if isinstance(insights_data, dict) and "error" in insights_data:
        error_msg = insights_data["error"]
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Insights - Error</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f7fa;
                }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .error {{
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    border-left: 4px solid #f44336;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">
                    <h2>❌ Error</h2>
                    <p>{error_msg}</p>
                    <a href="/dashboard">← Back to Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """)
    
    insights_text = insights_data.get("insights", "").replace("\n", "<br>")
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Insights - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
            }}
            .insights-card {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                line-height: 1.8;
            }}
            .insights-header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                margin-bottom: 20px;
            }}
            .loading {{
                text-align: center;
                padding: 40px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/ai-insights-view">🤖 AI Insights</a>
            </div>
            
            <div class="insights-header">
                <h1>🤖 AI Health Coach</h1>
                <p>Personalized insights powered by {ai_model}</p>
            </div>
            
            <div class="insights-card">
                {insights_text}
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/ai-insights")
async def ai_insights():
    """Get AI-powered insights from your WHOOP data using Ollama or OpenAI"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    if not ai_client:
        return {"error": "No AI client configured. Install Ollama or add OPENAI_API_KEY to .env file"}
    
    print(f"\n🤖 Generating AI insights using {ai_model}...")
    
    async with httpx.AsyncClient() as client:
        # Fetch latest recovery
        recovery_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "3"}  # Get last 3 cycles for trend analysis
        )
        
        # Fetch latest sleep
        sleep_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/activity/sleep",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "3"}
        )
        
        # Fetch latest workouts
        workout_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/workout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "5"}
        )
    
    if recovery_response.status_code != 200:
        return {"error": "Could not fetch cycle data", "details": recovery_response.text}
    
    cycles_data = recovery_response.json()
    sleep_data = sleep_response.json() if sleep_response.status_code == 200 else {"records": []}
    workout_data = workout_response.json() if workout_response.status_code == 200 else {"records": []}
    
    # Prepare data summary for AI
    data_summary = f"""
WHOOP Data Summary:

Recent Cycles (last 3):
{cycles_data}

Recent Sleep (last 3):
{sleep_data}

Recent Workouts (last 5):
{workout_data}
"""
    
    try:
        # Call AI API (Ollama or OpenAI)
        response = ai_client.chat.completions.create(
            model=ai_model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a professional health and fitness coach analyzing WHOOP biometric data. 
                    Provide personalized, actionable insights based on the user's recovery, sleep, and workout data.
                    Focus on:
                    1. Current recovery status and what it means
                    2. Sleep quality and patterns
                    3. Workout recommendations (should they train hard, take it easy, or rest?)
                    4. Trends and patterns over the last few days
                    5. Specific actionable advice
                    
                    Be concise, encouraging, and data-driven. Use bullet points for clarity."""
                },
                {
                    "role": "user",
                    "content": f"Analyze my WHOOP data and provide insights:\n\n{data_summary}"
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        ai_insights = response.choices[0].message.content
        print("✅ AI insights generated!")
        
        return {
            "insights": ai_insights,
            "data_summary": {
                "cycles_count": len(cycles_data.get("records", [])),
                "sleep_count": len(sleep_data.get("records", [])),
                "workout_count": len(workout_data.get("records", []))
            }
        }
    
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        return {"error": f"Failed to generate insights: {str(e)}"}

@app.get("/cycles-view")
async def cycles_view():
    """HTML view for cycles data"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "7"}
        )
    
    if response.status_code != 200:
        return HTMLResponse("<h1>Error fetching cycles</h1>")
    
    data = response.json()
    cycles = data.get("records", [])
    
    cycles_html = ""
    for cycle in cycles:
        cycle_id = cycle.get("id")
        strain = cycle.get("score", {}).get("strain")
        is_complete = cycle.get("end") is not None
        
        # Display note for current/incomplete cycles
        status_note = "" if is_complete else " (Current - in progress)"
        
        cycles_html += f"""
        <div class="cycle-card">
            <div class="cycle-date">📅 {cycle.get('start', '')[:10]}{status_note}</div>
            <div class="cycle-metrics">
                <div class="mini-metric">
                    <span class="mini-label">Strain</span>
                    <span class="mini-value">{f'{strain:.1f}' if strain else 'N/A'}</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">Status</span>
                    <span class="mini-value" style="font-size: 0.9em;">{'Complete' if is_complete else 'Active'}</span>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 0.85em; color: #666;">
                {'Recovery & sleep data available after cycle completes' if not is_complete else 'View recovery-view for recovery data'}
            </div>
        </div>
        """
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cycles - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .cycles-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }}
            .cycle-card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .cycle-date {{
                font-size: 1.1em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }}
            .cycle-metrics {{
                display: flex;
                gap: 15px;
            }}
            .mini-metric {{
                flex: 1;
                text-align: center;
            }}
            .mini-label {{
                display: block;
                font-size: 0.8em;
                color: #666;
                margin-bottom: 5px;
            }}
            .mini-value {{
                display: block;
                font-size: 1.5em;
                font-weight: bold;
            }}
            .recovery-green {{ color: #4caf50; }}
            .recovery-yellow {{ color: #ff9800; }}
            .recovery-red {{ color: #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/cycles-view">🔄 Cycles</a>
                <a href="/ai-insights-view">🤖 AI Insights</a>
            </div>
            
            <div class="header">
                <h1>🔄 Your Cycles</h1>
                <p>Last 7 days of recovery, strain, and sleep</p>
            </div>
            
            <div class="cycles-grid">
                {cycles_html}
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/recovery-view")
async def recovery_view():
    """HTML view for recovery data"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    async with httpx.AsyncClient() as client:
        cycle_response = await client.get(
            "https://api.prod.whoop.com/developer/v1/cycle",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "1"}
        )
    
    if cycle_response.status_code != 200:
        return HTMLResponse("<h1>Error fetching cycle data</h1>")
    
    cycle_data = cycle_response.json()
    
    if not cycle_data.get("records") or len(cycle_data["records"]) == 0:
        return HTMLResponse("<h1>No cycle data available</h1>")
    
    latest_cycle = cycle_data["records"][0]
    cycle_id = latest_cycle["id"]
    
    async with httpx.AsyncClient() as client:
        recovery_response = await client.get(
            f"https://api.prod.whoop.com/developer/v1/cycle/{cycle_id}/recovery",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
    
    if recovery_response.status_code == 404:
        message = "No recovery data available for your current cycle yet. Check back after you've slept!"
        recovery = None
    elif recovery_response.status_code == 200:
        recovery = recovery_response.json()
        message = None
    else:
        return HTMLResponse("<h1>Error fetching recovery data</h1>")
    
    recovery_score = recovery.get("score", {}).get("recovery_score") if recovery else None
    hrv = recovery.get("score", {}).get("hrv_rmssd_milli") if recovery else None
    rhr = recovery.get("score", {}).get("resting_heart_rate") if recovery else None
    
    recovery_class = "recovery-green" if recovery_score and recovery_score >= 67 else "recovery-yellow" if recovery_score and recovery_score >= 34 else "recovery-red"
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Recovery - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .recovery-main {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .recovery-score {{
                font-size: 5em;
                font-weight: bold;
                margin: 20px 0;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }}
            .metric-card {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .metric-label {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 10px;
            }}
            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #333;
            }}
            .recovery-green {{ color: #4caf50; }}
            .recovery-yellow {{ color: #ff9800; }}
            .recovery-red {{ color: #f44336; }}
            .message {{
                background: #fff3cd;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/recovery-view">❤️ Recovery</a>
            </div>
            
            <div class="header">
                <h1>❤️ Recovery Status</h1>
                <p>Your body's readiness to perform</p>
            </div>
            
            {f'<div class="message">{message}</div>' if message else ''}
            
            <div class="recovery-main">
                <div class="recovery-score {recovery_class}">
                    {f'{recovery_score}%' if recovery_score else 'N/A'}
                </div>
                <div style="color: #666; font-size: 1.2em;">
                    Recovery Score
                </div>
            </div>
            
            {f'''<div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">❤️ Resting Heart Rate</div>
                    <div class="metric-value">{rhr if rhr else 'N/A'}</div>
                    <div style="color: #666; font-size: 0.9em;">bpm</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">📊 HRV</div>
                    <div class="metric-value">{hrv if hrv else 'N/A'}</div>
                    <div style="color: #666; font-size: 0.9em;">ms</div>
                </div>
            </div>''' if recovery else ''}
        </div>
    </body>
    </html>
    """)

@app.get("/workouts-view")
async def workouts_view():
    """HTML view for workouts"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/workout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "10"}
        )
    
    print(f"\n💪 Workouts API Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return HTMLResponse(f"<h1>Error fetching workouts</h1><p>Status: {response.status_code}</p><p>{response.text}</p>")
    
    data = response.json()
    workouts = data.get("records", [])
    
    workouts_html = ""
    for workout in workouts:
        sport_name = workout.get("sport_name", "Unknown")
        strain = workout.get("score", {}).get("strain")
        avg_hr = workout.get("score", {}).get("average_heart_rate")
        max_hr = workout.get("score", {}).get("max_heart_rate")
        calories = workout.get("score", {}).get("kilojoule")
        start_time = workout.get("start", "")[:10]
        
        workouts_html += f"""
        <div class="workout-card">
            <div class="workout-header">
                <div class="workout-sport">💪 {sport_name}</div>
                <div class="workout-date">{start_time}</div>
            </div>
            <div class="workout-metrics">
                <div class="mini-metric">
                    <span class="mini-label">Strain</span>
                    <span class="mini-value">{f'{strain:.1f}' if strain else 'N/A'}</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">Avg HR</span>
                    <span class="mini-value">{avg_hr if avg_hr else 'N/A'}</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">Max HR</span>
                    <span class="mini-value">{max_hr if max_hr else 'N/A'}</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">kJ</span>
                    <span class="mini-value">{int(calories) if calories else 'N/A'}</span>
                </div>
            </div>
        </div>
        """
    
    if not workouts_html:
        workouts_html = '<div class="message">No workouts found. Start tracking your activities!</div>'
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Workouts - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .workout-card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }}
            .workout-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }}
            .workout-sport {{
                font-size: 1.2em;
                font-weight: 600;
                color: #333;
            }}
            .workout-date {{
                color: #666;
            }}
            .workout-metrics {{
                display: flex;
                gap: 20px;
            }}
            .mini-metric {{
                flex: 1;
                text-align: center;
                padding: 10px;
                background: #f5f7fa;
                border-radius: 8px;
            }}
            .mini-label {{
                display: block;
                font-size: 0.8em;
                color: #666;
                margin-bottom: 5px;
            }}
            .mini-value {{
                display: block;
                font-size: 1.3em;
                font-weight: bold;
                color: #667eea;
            }}
            .message {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/workouts-view">💪 Workouts</a>
            </div>
            
            <div class="header">
                <h1>💪 Your Workouts</h1>
                <p>Recent training activities</p>
            </div>
            
            {workouts_html}
        </div>
    </body>
    </html>
    """)

@app.get("/sleep-view")
async def sleep_view():
    """HTML view for sleep data"""
    if "access_token" not in tokens:
        return RedirectResponse("/")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.prod.whoop.com/developer/v1/activity/sleep",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            params={"limit": "7"}
        )
    
    print(f"\n😴 Sleep API Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return HTMLResponse(f"<h1>Error fetching sleep data</h1><p>Status: {response.status_code}</p><p>{response.text}</p>")
    
    data = response.json()
    sleeps = data.get("records", [])
    
    sleep_html = ""
    for sleep in sleeps:
        score = sleep.get("score", {})
        sleep_perf = score.get("sleep_performance_percentage")
        duration_ms = sleep.get("score", {}).get("total_sleep_time_milli", 0)
        duration_hours = duration_ms / (1000 * 60 * 60) if duration_ms else 0
        efficiency = score.get("sleep_efficiency_percentage")
        start_time = sleep.get("start", "")[:10]
        
        perf_class = "recovery-green" if sleep_perf and sleep_perf >= 85 else "recovery-yellow" if sleep_perf and sleep_perf >= 70 else "recovery-red"
        
        sleep_html += f"""
        <div class="sleep-card">
            <div class="sleep-date">😴 {start_time}</div>
            <div class="sleep-metrics">
                <div class="mini-metric">
                    <span class="mini-label">Performance</span>
                    <span class="mini-value {perf_class}">{sleep_perf}%</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">Duration</span>
                    <span class="mini-value">{duration_hours:.1f}h</span>
                </div>
                <div class="mini-metric">
                    <span class="mini-label">Efficiency</span>
                    <span class="mini-value">{efficiency}%</span>
                </div>
            </div>
        </div>
        """
    
    if not sleep_html:
        sleep_html = '<div class="message">No sleep data found.</div>'
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sleep - WHOOP</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f7fa;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .nav-bar {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .nav-bar a {{
                padding: 10px 20px;
                margin-right: 10px;
                border-radius: 6px;
                text-decoration: none;
                color: #667eea;
                font-weight: 600;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .sleep-card {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }}
            .sleep-date {{
                font-size: 1.1em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }}
            .sleep-metrics {{
                display: flex;
                gap: 15px;
            }}
            .mini-metric {{
                flex: 1;
                text-align: center;
                padding: 15px;
                background: #f5f7fa;
                border-radius: 8px;
            }}
            .mini-label {{
                display: block;
                font-size: 0.8em;
                color: #666;
                margin-bottom: 5px;
            }}
            .mini-value {{
                display: block;
                font-size: 1.5em;
                font-weight: bold;
            }}
            .recovery-green {{ color: #4caf50; }}
            .recovery-yellow {{ color: #ff9800; }}
            .recovery-red {{ color: #f44336; }}
            .message {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-bar">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/sleep-view">😴 Sleep</a>
            </div>
            
            <div class="header">
                <h1>😴 Your Sleep</h1>
                <p>Last 7 nights of sleep data</p>
            </div>
            
            {sleep_html}
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    print("="*60)
    print("🚀 Starting WHOOP OAuth Server")
    print("="*60)
    print(f"Server URL: http://localhost:3000")
    print(f"ngrok URL: {NGROK_URL}")
    print(f"Callback URL: {NGROK_URL}/callback")
    print("="*60)
    print("\n📋 STEPS:")
    print("1. Make sure ngrok is running: ngrok http 3000")
    print("2. Open browser: http://localhost:3000")
    print("3. Click 'Click here to login with WHOOP'")
    print("4. Watch this terminal for logs")
    print("="*60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=3000, log_level="info")
