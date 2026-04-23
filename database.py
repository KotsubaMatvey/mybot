"""SQLite persistence for users, subscriptions, and preferences."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

DEFAULT_ENTRY_MODELS = ["Entry Model 1", "Entry Model 2", "Entry Model 3"]
DEFAULT_TRADE_DIRECTIONS = ["long", "short"]

_USER_COLUMNS: dict[str, str] = {
    "user_id": "INTEGER PRIMARY KEY",
    "symbols": "TEXT DEFAULT '[]'",
    "patterns": "TEXT DEFAULT '[]'",
    "timeframes": "TEXT DEFAULT '[]'",
    "active": "INTEGER DEFAULT 0",
    "setup_done": "INTEGER DEFAULT 0",
    "confluence": "INTEGER DEFAULT 1",
    "expires_at": "TEXT DEFAULT NULL",
    "invoice_id": "INTEGER DEFAULT NULL",
    "is_owner": "INTEGER DEFAULT 0",
    "sessions_alerts": "INTEGER DEFAULT 0",
    "charts_enabled": "INTEGER DEFAULT 0",
    "entry_models": """TEXT DEFAULT '["Entry Model 1", "Entry Model 2", "Entry Model 3"]'""",
    "trade_directions": """TEXT DEFAULT '["long", "short"]'""",
}
_JSON_COLUMNS = {"symbols", "patterns", "timeframes", "entry_models", "trade_directions"}
_BOOL_COLUMNS = {"active", "setup_done", "confluence", "is_owner", "sessions_alerts", "charts_enabled"}


def get_conn() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
            """
        )
        existing_columns = _get_existing_columns(conn, "users")
        for column, definition in _USER_COLUMNS.items():
            if column in existing_columns:
                continue
            conn.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        conn.commit()


def _get_existing_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def upsert_user(user_id: int, **kwargs: Any) -> None:
    invalid = set(kwargs) - (set(_USER_COLUMNS) - {"user_id"})
    if invalid:
        raise ValueError(f"upsert_user: unknown column(s): {sorted(invalid)}")

    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        if kwargs:
            assignments = ", ".join(f"{column}=?" for column in kwargs)
            values = [_db_value(column, value) for column, value in kwargs.items()]
            conn.execute(f"UPDATE users SET {assignments} WHERE user_id=?", (*values, user_id))
        conn.commit()


def get_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        return None
    return _row_to_user(row)


def get_all_active_users() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users WHERE active=1 AND setup_done=1").fetchall()
    return [_row_to_active_user(row) for row in rows if _has_live_access_row(row)]


def get_session_alert_users() -> list[int]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE active=1 AND setup_done=1 AND sessions_alerts=1"
        ).fetchall()
    return [row["user_id"] for row in rows if _has_live_access_row(row)]


def save_preferences(
    user_id: int,
    symbols: set[str],
    patterns: set[str],
    timeframes: set[str],
    entry_models: set[str] | None = None,
    trade_directions: set[str] | None = None,
) -> None:
    upsert_user(
        user_id,
        symbols=sorted(symbols),
        patterns=sorted(patterns),
        timeframes=sorted(timeframes),
        entry_models=sorted(entry_models or DEFAULT_ENTRY_MODELS),
        trade_directions=sorted(trade_directions or DEFAULT_TRADE_DIRECTIONS),
        active=1,
        setup_done=1,
    )


def set_active(user_id: int, active: bool) -> None:
    upsert_user(user_id, active=int(active))


def set_subscription(user_id: int, days: int) -> None:
    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    upsert_user(user_id, expires_at=expires_at)


def set_owner(user_id: int) -> None:
    upsert_user(user_id, is_owner=1)


def is_subscribed(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    if user.get("is_owner"):
        return True
    expires_at = user.get("expires_at")
    if not expires_at:
        return False
    try:
        return datetime.now(timezone.utc) < datetime.fromisoformat(expires_at)
    except ValueError:
        return False


def get_subscription_status(user_id: int) -> str:
    user = get_user(user_id)
    if not user:
        return "No subscription"
    if user.get("is_owner"):
        return "Owner - lifetime access"
    expires_at = user.get("expires_at")
    if not expires_at:
        return "No active subscription"
    try:
        expiry = datetime.fromisoformat(expires_at)
    except ValueError:
        return "Unknown"

    now = datetime.now(timezone.utc)
    if now >= expiry:
        return "Subscription expired"
    days_left = max(1, int((expiry - now).total_seconds() // 86400 + 0.999))
    return f"Active - {days_left} days remaining"


def toggle_sessions_alerts(user_id: int) -> bool:
    user = get_user(user_id)
    new_value = not user.get("sessions_alerts", False) if user else True
    upsert_user(user_id, sessions_alerts=int(new_value))
    return new_value


def toggle_charts(user_id: int) -> bool:
    user = get_user(user_id)
    new_value = not user.get("charts_enabled", False) if user else True
    upsert_user(user_id, charts_enabled=int(new_value))
    return new_value


def _row_to_user(row: sqlite3.Row) -> dict:
    return {
        "user_id": row["user_id"],
        "symbols": _load_json_set(row["symbols"]),
        "patterns": _load_json_set(row["patterns"]),
        "timeframes": _load_json_set(row["timeframes"]),
        "entry_models": _load_json_set(row["entry_models"], DEFAULT_ENTRY_MODELS),
        "trade_directions": _load_json_set(row["trade_directions"], DEFAULT_TRADE_DIRECTIONS),
        "active": bool(row["active"]),
        "setup_done": bool(row["setup_done"]),
        "confluence": True if row["confluence"] is None else bool(row["confluence"]),
        "expires_at": row["expires_at"],
        "invoice_id": row["invoice_id"],
        "is_owner": bool(row["is_owner"]),
        "sessions_alerts": bool(row["sessions_alerts"]),
        "charts_enabled": bool(row["charts_enabled"]),
    }


def _row_to_active_user(row: sqlite3.Row) -> dict:
    user = _row_to_user(row)
    return {
        "user_id": user["user_id"],
        "symbols": user["symbols"],
        "patterns": user["patterns"],
        "timeframes": user["timeframes"],
        "entry_models": user["entry_models"],
        "trade_directions": user["trade_directions"],
        "charts_enabled": user["charts_enabled"],
    }


def _load_json_set(raw: str | None, default: list[str] | None = None) -> set[str]:
    if not raw:
        return set(default or [])
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return set(default or [])
    if isinstance(value, list):
        return {str(item) for item in value}
    return set(default or [])


def _db_value(column: str, value: Any) -> Any:
    if column in _JSON_COLUMNS:
        if isinstance(value, set):
            value = sorted(value)
        return json.dumps(list(value) if isinstance(value, list) else value)
    if column in _BOOL_COLUMNS:
        return int(bool(value))
    return value


def _has_live_access_row(row: sqlite3.Row) -> bool:
    if bool(row["is_owner"]):
        return True
    expires_at = row["expires_at"]
    if not expires_at:
        return False
    try:
        return datetime.now(timezone.utc) < datetime.fromisoformat(expires_at)
    except ValueError:
        return False


__all__ = [
    "DB_PATH",
    "DEFAULT_ENTRY_MODELS",
    "DEFAULT_TRADE_DIRECTIONS",
    "get_all_active_users",
    "get_conn",
    "get_session_alert_users",
    "get_subscription_status",
    "get_user",
    "init_db",
    "is_subscribed",
    "save_preferences",
    "set_active",
    "set_owner",
    "set_subscription",
    "toggle_charts",
    "toggle_sessions_alerts",
    "upsert_user",
]
