from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from .config import settings
from .auth import router as auth_router, get_session_token, add_session_middleware
from .whoop_api import api_get, fetch_paginated

app = FastAPI(title="Agera × WHOOP", version="0.1.0")
add_session_middleware(app)
app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h2>Agera × WHOOP (FastAPI)</h2>
    <ul>
      <li><a href="/login">Connect WHOOP</a></li>
      <li><a href="/me">My profile & body measurements</a></li>
      <li><a href="/daily">Today cycles</a> (use <code>?day=YYYY-MM-DD</code>)</li>
      <li><a href="/workouts?start=2026-01-01T00:00:00Z&end=2026-02-01T00:00:00Z">Workouts (range)</a></li>
      <li><a href="/test-session">Test Session</a></li>
    </ul>
    """

@app.get("/test-session")
async def test_session(request: Request):
    # Test if sessions are working
    count = request.session.get("count", 0)
    count += 1
    request.session["count"] = count
    return JSONResponse({"session_works": True, "count": count, "session_data": dict(request.session)})

@app.get("/me")
async def me(request: Request):
    token = get_session_token(request)
    if not token:
        return RedirectResponse("/login")
    profile = await api_get(token, "/v1/user/profile/basic")
    body = await api_get(token, "/v1/user/profile/body_measurements/latest")
    return JSONResponse({"profile": profile, "body_measurements": body})

@app.get("/daily")
async def daily(request: Request, day: str | None = None):
    token = get_session_token(request)
    if not token:
        return RedirectResponse("/login")
    day = day or date.today().isoformat()
    cycles = await api_get(token, "/v1/cycles", {
        "start": f"{day}T00:00:00Z",
        "end": f"{day}T23:59:59Z"
    })
    return JSONResponse({"day": day, "cycles": cycles})

@app.get("/workouts")
async def workouts(request: Request, start: str, end: str):
    token = get_session_token(request)
    if not token:
        return RedirectResponse("/login")
    records = await fetch_paginated(token, "/v1/workouts", {"start": start, "end": end})
    return JSONResponse({"count": len(records), "workouts": records})

# Webhook stub — configure URL in WHOOP console later
@app.post("/webhooks/whoop")
async def webhooks(req: Request):
    payload = await req.json()
    # TODO: verify signatures if WHOOP provides; process events
    return JSONResponse({"ok": True, "received": payload})

Sunday, February 1, 2026 10:23:28 PM

