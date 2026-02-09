"""WHOOP MCP Server - Exposes WHOOP API data as MCP tools.

This server wraps the existing WHOOP API integration and exposes it as
Model Context Protocol tools that can be used by AI assistants like Claude.

Run with: python whoop_mcp_server.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Initialize MCP server
server = Server("whoop-fitness")

# WHOOP API configuration
API_BASE = "https://api.prod.whoop.com/developer/v2"
# Use absolute path so it works regardless of working directory
TOKEN_CACHE_FILE = Path(__file__).parent / ".token_cache.json"

# Log to stderr for debugging (stdout is used for MCP protocol)
def debug_log(message: str):
    """Log debug messages to stderr."""
    print(f"[WHOOP-MCP] {message}", file=sys.stderr, flush=True)


def load_token() -> str | None:
    """Load cached OAuth token from file."""
    token_file = TOKEN_CACHE_FILE
    debug_log(f"Looking for token at: {token_file}")
    debug_log(f"Token file exists: {token_file.exists()}")
    
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                data = json.load(f)
                token = data.get('access_token')
                if token:
                    debug_log(f"Token loaded successfully (length: {len(token)})")
                    return token
                else:
                    debug_log("ERROR: No access_token field in token file")
        except Exception as e:
            debug_log(f"ERROR loading token: {e}")
    else:
        debug_log(f"ERROR: Token file not found at {token_file}")
    return None


async def make_api_request(endpoint: str) -> dict[str, Any]:
    """Make authenticated request to WHOOP API."""
    token = load_token()
    if not token:
        debug_log("ERROR: No access token available")
        return {"error": "No access token found. Please authenticate via the FastAPI server first."}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"message": "Data not available yet. This data may still be syncing or not yet calculated by WHOOP.", "status": 404}
            else:
                return {"error": f"API error {e.response.status_code}: {e.response.text}"}
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}


# Register tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_user_profile",
            description="Get WHOOP user profile information including user ID, email, and basic profile data",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_recovery_score",
            description="Get latest recovery score with details like HRV, resting heart rate, and sleep performance. Optionally filter by date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ago": {"type": "integer", "description": "Get recovery from N days ago (e.g., 1 for yesterday, 2 for day before)", "default": 0}
                }
            }
        ),
        Tool(
            name="get_current_strain",
            description="Get current day strain including overall strain score and calorie breakdown",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_recent_cycles",
            description="Get recent physiological cycles with recovery, strain, and sleep data",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of cycles to return (default 7)", "default": 7}
                }
            }
        ),
        Tool(
            name="get_latest_sleep",
            description="Get most recent sleep data including duration, efficiency, and stages. Optionally filter by date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ago": {"type": "integer", "description": "Get sleep from N days ago (e.g., 1 for yesterday, 2 for day before)", "default": 0}
                }
            }
        ),
        Tool(
            name="get_recent_workouts",
            description="Get recent workout activities with strain and duration",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of workouts to return (default 10)", "default": 10}
                }
            }
        ),
        Tool(
            name="get_body_measurements",
            description="Get body measurements including height and weight",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_health_summary",
            description="Get comprehensive health summary with latest strain, recovery, and sleep",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_user_profile":
        result = await get_user_profile()
    elif name == "get_recovery_score":
        days_ago = arguments.get("days_ago", 0)
        result = await get_recovery_score(days_ago)
    elif name == "get_current_strain":
        result = await get_current_strain()
    elif name == "get_recent_cycles":
        limit = arguments.get("limit", 7)
        result = await get_recent_cycles(limit)
    elif name == "get_latest_sleep":
        days_ago = arguments.get("days_ago", 0)
        result = await get_latest_sleep(days_ago)
    elif name == "get_recent_workouts":
        limit = arguments.get("limit", 10)
        result = await get_recent_workouts(limit)
    elif name == "get_body_measurements":
        result = await get_body_measurements()
    elif name == "get_health_summary":
        result = await get_health_summary()
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_user_profile() -> dict[str, Any]:
    """Get WHOOP user profile information.
    
    Returns user ID, email, and basic profile data.
    """
    return await make_api_request("/user/profile/basic")


async def get_recovery_score(days_ago: int = 0) -> dict[str, Any]:
    """Get the recovery score.
    
    Args:
        days_ago: Number of days back to retrieve (0=today, 1=yesterday, etc.)
    
    Recovery score indicates how ready your body is for strain.
    Returns recovery percentage, HRV, RHR, and sleep performance.
    Note: Only available for completed sleep cycles.
    """
    from datetime import datetime, timedelta, timezone
    
    if days_ago == 0:
        # Get most recent recovery
        recovery_data = await make_api_request("/recovery?limit=1")
    else:
        # Get recovery for specific day using date range
        # Calculate date range for the specific day
        target_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        start_str = start_date.isoformat().replace('+00:00', 'Z')
        end_str = end_date.isoformat().replace('+00:00', 'Z')
        
        recovery_data = await make_api_request(f"/recovery?start={start_str}&end={end_str}")
    
    if "error" in recovery_data or "message" in recovery_data:
        return recovery_data
    
    records = recovery_data.get("records", [])
    if not records:
        day_desc = "today" if days_ago == 0 else f"{days_ago} day(s) ago"
        return {"message": f"No recovery data available for {day_desc}. Recovery is calculated after completing a sleep session."}
    
    return records[0]


async def get_current_strain() -> dict[str, Any]:
    """Get current day strain score.
    
    Strain measures cardiovascular load and workout intensity (0-21 scale).
    Returns strain score, kilojoules, and average heart rate.
    """
    cycles_data = await make_api_request("/cycle")
    if "error" in cycles_data:
        return cycles_data
    
    cycles = cycles_data.get("records", [])
    if not cycles:
        return {"message": "No cycles found"}
    
    # Get current (most recent) cycle
    current_cycle = cycles[0]
    return {
        "cycle_id": current_cycle["id"],
        "start": current_cycle["start"],
        "end": current_cycle.get("end"),
        "strain": current_cycle.get("score", {}).get("strain"),
        "kilojoules": current_cycle.get("score", {}).get("kilojoule"),
        "average_heart_rate": current_cycle.get("score", {}).get("average_heart_rate")
    }


async def get_recent_cycles(limit: int = 7) -> dict[str, Any]:
    """Get recent physiological cycles with recovery data.
    
    Args:
        limit: Number of cycles to return (default 7)
    
    Each cycle represents a 24-hour period from wake to wake.
    Returns cycle ID, start/end times, strain, recovery, and status.
    """
    # Fetch cycles
    cycles_data = await make_api_request(f"/cycle?limit={limit}")
    if "error" in cycles_data:
        return cycles_data
    
    # Fetch recoveries
    recovery_data = await make_api_request(f"/recovery?limit={limit}")
    
    # Create a map of cycle_id -> recovery data
    recovery_map = {}
    if "error" not in recovery_data and "message" not in recovery_data:
        for r in recovery_data.get("records", []):
            cycle_id = r.get("cycle_id")
            if cycle_id:
                recovery_map[cycle_id] = {
                    "recovery_score": r.get("score", {}).get("recovery_score"),
                    "resting_heart_rate": r.get("score", {}).get("resting_heart_rate"),
                    "hrv_rmssd_milli": r.get("score", {}).get("hrv_rmssd_milli"),
                    "spo2_percentage": r.get("score", {}).get("spo2_percentage"),
                    "skin_temp_celsius": r.get("score", {}).get("skin_temp_celsius"),
                    "score_state": r.get("score_state")
                }
    
    # Combine cycle and recovery data
    cycles = cycles_data.get("records", [])
    enriched_cycles = []
    for c in cycles:
        cycle_id = c["id"]
        cycle_info = {
            "id": cycle_id,
            "start": c["start"],
            "end": c.get("end"),
            "strain": c.get("score", {}).get("strain"),
            "kilojoules": c.get("score", {}).get("kilojoule"),
            "average_heart_rate": c.get("score", {}).get("average_heart_rate"),
            "max_heart_rate": c.get("score", {}).get("max_heart_rate"),
            "status": "completed" if c.get("end") else "active"
        }
        
        # Add recovery data if available
        if cycle_id in recovery_map:
            cycle_info["recovery"] = recovery_map[cycle_id]
        else:
            cycle_info["recovery"] = None
        
        enriched_cycles.append(cycle_info)
    
    return {
        "count": len(enriched_cycles),
        "cycles": enriched_cycles
    }


async def get_latest_sleep(days_ago: int = 0) -> dict[str, Any]:
    """Get sleep data.
    
    Args:
        days_ago: Number of days back to retrieve (0=today, 1=yesterday, etc.)
    
    Returns sleep duration, quality score, efficiency, disturbances,
    respiratory rate, and sleep stages breakdown.
    Note: Only available for completed sleep sessions.
    """
    from datetime import datetime, timedelta, timezone
    
    if days_ago == 0:
        # Get most recent sleep
        sleep_data = await make_api_request("/activity/sleep?limit=1")
    else:
        # Get sleep for specific day using date range
        target_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        start_str = start_date.isoformat().replace('+00:00', 'Z')
        end_str = end_date.isoformat().replace('+00:00', 'Z')
        
        sleep_data = await make_api_request(f"/activity/sleep?start={start_str}&end={end_str}")
    
    if "error" in sleep_data or "message" in sleep_data:
        return sleep_data
    
    records = sleep_data.get("records", [])
    if not records:
        day_desc = "today" if days_ago == 0 else f"{days_ago} day(s) ago"
        return {"message": f"No sleep data available for {day_desc}. Sleep data is recorded after you complete a sleep session."}
    
    return records[0]


async def get_recent_workouts(limit: int = 5) -> dict[str, Any]:
    """Get recent workout activities.
    
    Args:
        limit: Number of workouts to return (default 5)
    
    Returns workout type, duration, strain, average HR, max HR, and calories.
    """
    workouts_data = await make_api_request(f"/activity/workout?limit={limit}")
    if "error" in workouts_data or "message" in workouts_data:
        return workouts_data
    
    workouts = workouts_data.get("records", [])
    if not workouts:
        return {"message": "No workout data available yet."}
    
    return {
        "count": len(workouts),
        "workouts": workouts
    }
    return {
        "count": len(workouts),
        "workouts": [
            {
                "id": w["id"],
                "sport": w.get("sport_id"),
                "start": w["start"],
                "end": w["end"],
                "strain": w.get("score", {}).get("strain"),
                "average_heart_rate": w.get("score", {}).get("average_heart_rate"),
                "max_heart_rate": w.get("score", {}).get("max_heart_rate"),
                "kilojoules": w.get("score", {}).get("kilojoule")
            }
            for w in workouts
        ]
    }


async def get_body_measurements() -> dict[str, Any]:
    """Get body measurement data.
    
    Returns height, weight, and max heart rate if available.
    """
    return await make_api_request("/user/measurement/body")


async def get_health_summary() -> dict[str, Any]:
    """Get comprehensive health summary.
    
    Returns current strain, latest recovery (if available), and recent sleep.
    This is a convenient single call to get overall health status.
    """
    # Get all data in parallel
    profile_task = get_user_profile()
    strain_task = get_current_strain()
    recovery_task = get_recovery_score()
    sleep_task = get_latest_sleep()
    
    profile, strain, recovery, sleep = await asyncio.gather(
        profile_task, strain_task, recovery_task, sleep_task
    )
    
    return {
        "user": profile,
        "current_strain": strain,
        "latest_recovery": recovery,
        "latest_sleep": sleep
    }


async def main():
    """Entry point for the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
