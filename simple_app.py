"""
Simple WHOOP OAuth app - minimal implementation with in-memory state
"""
import os
import secrets
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Store state in memory (not for production!)
oauth_states = {}
access_tokens = {}

# WHOOP OAuth config
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
REDIRECT_URI = f"{PUBLIC_BASE_URL}/callback"

WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
WHOOP_API_BASE = "https://api.prod.whoop.com"

SCOPES = "read:profile read:body_measurement read:cycles read:workout read:sleep read:recovery"

print(f"SERVER STARTING - Redirect URI: {REDIRECT_URI}")

@app.get("/")
async def home():
    return HTMLResponse("""
        <h1>WHOOP API - Simple OAuth</h1>
        <p><a href="/login">Login with WHOOP</a></p>
    """)

@app.get("/login")
async def login(request: Request):
    print("\n" + "="*50)
    print("LOGIN REQUEST RECEIVED")
    print("="*50)
    
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True  # Store state in memory
    print(f"Generated state: {state}")
    print(f"Stored states count: {len(oauth_states)}")
    
    auth_url = (
        f"{WHOOP_AUTH_URL}?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPES}&"
        f"state={state}"
    )
    print(f"Redirecting to WHOOP...")
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    print("\n" + "="*50)
    print("CALLBACK REQUEST RECEIVED!")
    print("="*50)
    
    try:
        # Get state and code from URL
        state = request.query_params.get("state")
        code = request.query_params.get("code")
        
        print(f"State from URL: {state}")
        print(f"Code from URL: {code[:20] if code else None}...")
        print(f"Valid states in memory: {list(oauth_states.keys())[:3]}")
        
        # Verify state
        if not state or state not in oauth_states:
            print("ERROR: Invalid state!")
            return JSONResponse({"error": "Invalid state", "received": state}, status_code=400)
        
        if not code:
            print("ERROR: No code received!")
            return JSONResponse({"error": "No code received"}, status_code=400)
        
        print("State validated! Exchanging code for token...")
        
        # Exchange code for token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        
        print(f"Posting to: {WHOOP_TOKEN_URL}")
        print(f"With redirect_uri: {REDIRECT_URI}")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(WHOOP_TOKEN_URL, data=token_data)
            
            print(f"Token response status: {token_response.status_code}")
            
            if token_response.status_code != 200:
                print(f"ERROR: Token exchange failed!")
                print(f"Response: {token_response.text}")
                return JSONResponse({
                    "error": "Token exchange failed",
                    "status": token_response.status_code,
                    "details": token_response.text
                }, status_code=500)
            
            token_json = token_response.json()
            access_token = token_json["access_token"]
            
            # Store token with state as key
            access_tokens[state] = access_token
            print("SUCCESS! Token received and stored!")
            print(f"Redirecting to /profile?state={state}")
        
        return RedirectResponse(f"/profile?state={state}")
        
    except Exception as e:
        print(f"EXCEPTION in callback: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/profile")
async def profile(request: Request):
    print("\n" + "="*50)
    print("PROFILE REQUEST RECEIVED")
    print("="*50)
    
    state = request.query_params.get("state")
    if not state or state not in access_tokens:
        print("No valid token found, redirecting to login")
        return RedirectResponse("/login")
    
    access_token = access_tokens[state]
    print(f"Found access token for state: {state}")
    
    async with httpx.AsyncClient() as client:
        # Get user profile
        print("Fetching user profile...")
        profile_response = await client.get(
            f"{WHOOP_API_BASE}/v2/user/profile/basic",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Get body measurements
        print("Fetching body measurements...")
        body_response = await client.get(
            f"{WHOOP_API_BASE}/v2/user/measurement/body",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Profile status: {profile_response.status_code}")
        print(f"Body status: {body_response.status_code}")
        
        return JSONResponse({
            "success": True,
            "profile": profile_response.json() if profile_response.status_code == 200 else None,
            "body_measurements": body_response.json() if body_response.status_code == 200 else None,
        })

@app.get("/cycles")
async def cycles(request: Request, start: str = None, end: str = None):
    """Get cycles data. Example: /cycles?start=2026-01-01T00:00:00Z&end=2026-02-01T00:00:00Z"""
    access_token = request.session.get("access_token")
    if not access_token:
        return RedirectResponse("/login")
    
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WHOOP_API_BASE}/v2/cycle",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params
        )
        return JSONResponse(response.json() if response.status_code == 200 else {"error": response.text})

@app.get("/workouts")
async def workouts(request: Request, start: str = None, end: str = None):
    """Get workouts data. Example: /workouts?start=2026-01-01T00:00:00Z&end=2026-02-01T00:00:00Z"""
    access_token = request.session.get("access_token")
    if not access_token:
        return RedirectResponse("/login")
    
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{WHOOP_API_BASE}/v2/activity/workout",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params
        )
        return JSONResponse(response.json() if response.status_code == 200 else {"error": response.text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
