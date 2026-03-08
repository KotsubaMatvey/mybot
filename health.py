"""
health.py — simple HTTP health check server for VPS monitoring
Listens on port 8080. Returns 200 OK with bot status JSON.
Usage: curl http://localhost:8080/health
"""
import asyncio
import json
import logging
from aiohttp import web
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_state = {
    "started_at":    None,
    "last_scan":     None,
    "scan_count":    0,
    "alert_count":   0,
    "error_count":   0,
}


def record_scan():
    _state["last_scan"]  = datetime.now(timezone.utc).isoformat()
    _state["scan_count"] += 1


def record_alert():
    _state["alert_count"] += 1


def record_error():
    _state["error_count"] += 1


async def health_handler(request):
    now    = datetime.now(timezone.utc).isoformat()
    uptime = None
    if _state["started_at"]:
        delta   = datetime.now(timezone.utc) - _state["started_at"]
        uptime  = int(delta.total_seconds())

    payload = {
        "status":      "ok",
        "time":        now,
        "uptime_sec":  uptime,
        "scans":       _state["scan_count"],
        "alerts_sent": _state["alert_count"],
        "errors":      _state["error_count"],
        "last_scan":   _state["last_scan"],
    }
    return web.Response(
        text=json.dumps(payload, indent=2),
        content_type="application/json"
    )


async def start_health_server(port: int = 8080):
    _state["started_at"] = datetime.now(timezone.utc)
    app    = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/",       health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check server started on port {port}")
