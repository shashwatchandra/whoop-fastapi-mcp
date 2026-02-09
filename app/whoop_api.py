from typing import Any, Dict, Optional, List
import httpx
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception
from aiolimiter import AsyncLimiter
from fastapi import HTTPException
from .config import settings

# WHOOP rate limits: ~100/min, 10k/day. We cap to 90/min headroom.
minute_limiter = AsyncLimiter(90, 60)

def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return False

@retry(
    wait=wait_exponential_jitter(initial=1, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception(_is_retryable),
    reraise=True
)
async def api_get(token: dict, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Missing access token")
    async with minute_limiter, httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{settings.whoop_api_base}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token['access_token']}"}
        )
        if r.status_code >= 400:
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Let tenacity retry on retryable statuses
                raise e
        return r.json()

async def fetch_paginated(token: dict, path: str, params: Optional[Dict[str, Any]] = None, cursor_key: str = "next_token") -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    while True:
        q = dict(params or {})
        if cursor:
            q["cursor"] = cursor
        data = await api_get(token, path, q)
        records = data.get("records") or data.get("data") or []
        items.extend(records)
        cursor = data.get(cursor_key)
        if not cursor:
            break
    return items
