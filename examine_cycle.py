import json
import httpx
from pathlib import Path

TOKEN_CACHE_FILE = Path("c:/Shash/Agera/agera-fastapi/.token_cache.json")
data = json.load(open(TOKEN_CACHE_FILE))
token = data["access_token"]

API_BASE = "https://api.prod.whoop.com/developer/v1"

print("Examining cycle data structure...\n")

# Get a completed cycle
response = httpx.get(f"{API_BASE}/cycle/1298446459", headers={"Authorization": f"Bearer {token}"})
cycle = response.json()

print(json.dumps(cycle, indent=2))
