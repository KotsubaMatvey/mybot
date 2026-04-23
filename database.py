"""
SQLite database for persistent user subscriptions.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")
DEFAULT_ENTRY_MODELS = ["Entry Model 1", "Entry Model 2", "Entry Model 3"]
DEFAULT_TRADE_DIRECTIONS = ["long", "short"]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                symbols     TEXT DEFAULT '[]',
                patterns    TEXT DEFAULT '[]',
                timeframes  TEXT DEFAULT '[]',
                active      INTEGER DEFAULT 0,
                setup_done  INTEGER DEFAULT 0,
                confluence  INTEGER DEFAULT 1,
                expires_at  TEXT DEFAULT NULL,
                invoice_id  INTEGER DEFAULT NULL,
                is_owner         INTEGER DEFAULT 0,
                sessions_alerts  INTEGER DEFAULT 0,
                charts_enabled   INTEGER DEFAULT 0,
                entry_models     TEXT DEFAULT '["Entry Model 1", "Entry Model 2", "Entry Model 3"]',
                trade_directions TEXT DEFAULT '["long", "short"]'
            )
        """)
        # Migrations
        for col, definition in [
            ("confluence", "INTEGER DEFAULT 1"),
            ("expires_at",  "TEXT DEFAULT NULL"),
            ("invoice_id",  "INTEGER DEFAULT NULL"),
            ("is_owner",    "INTEGER DEFAULT 0"),
            ("sessions_alerts",  "INTEGER DEFAULT 0"),
            ("charts_enabled",  "INTEGER DEFAULT 0"),
            ("entry_models", """TEXT DEFAULT '["Entry Model 1", "Entry Model 2", "Entry Model 3"]'"""),
            ("trade_directions", """TEXT DEFAULT '["long", "short"]'"""),
        ]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
                conn.commit()
            except Exception:
                pass
        conn.commit()


_ALLOWED_COLUMNS = {
    "symbols", "patterns", "timeframes", "active", "setup_done",
    "confluence", "expires_at", "invoice_id", "is_owner",
    "sessions_alerts", "charts_enabled", "entry_models", "trade_directions",
}


def upsert_user(user_id: int, **kwargs):
    invalid = set(kwargs) - _ALLOWED_COLUMNS
    if invalid:
        raise ValueError(f"upsert_user: unknown column(s): {invalid}")
    with get_conn() as conn:
        existing = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not existing:
            conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        if kwargs:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            vals = [json.dumps(list(v)) if isinstance(v, (list, set)) else v for v in kwargs.values()]
            conn.execute(f"UPDATE users SET {sets} WHERE user_id=?", (*vals, user_id))
        conn.commit()


def get_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return None
        return {
            "user_id": row["user_id"],
            "symbols": set(json.loads(row["symbols"])),
            "patterns": set(json.loads(row["patterns"])),
            "timeframes": set(json.loads(row["timeframes"])),
            "entry_models": set(json.loads(row["entry_models"] or json.dumps(DEFAULT_ENTRY_MODELS))),
            "trade_directions": set(json.loads(row["trade_directions"] or json.dumps(DEFAULT_TRADE_DIRECTIONS))),
            "active": bool(row["active"]),
            "setup_done": bool(row["setup_done"]),
            "confluence": bool(row["confluence"]) if row["confluence"] is not None else True,
            "expires_at": row["expires_at"],
            "invoice_id": row["invoice_id"],
            "is_owner":         bool(row["is_owner"]) if row["is_owner"] is not None else False,
            "sessions_alerts":   bool(row["sessions_alerts"]) if row["sessions_alerts"] is not None else False,
            "charts_enabled":    bool(row["charts_enabled"])  if row["charts_enabled"]  is not None else False,
        }


def _has_live_access_row(row) -> bool:
    from datetime import datetime, timezone
    is_owner = bool(row["is_owner"]) if row["is_owner"] is not None else False
    if is_owner:
        return True
    expires = row["expires_at"]
    if not expires:
        return False
    try:
        return datetime.now(timezone.utc) < datetime.fromisoformat(expires)
    except Exception:
        return False


def get_all_active_users() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users WHERE active=1 AND setup_done=1").fetchall()
    result = []
    for r in rows:
        if not _has_live_access_row(r):
            continue
        result.append({
            "user_id":        r["user_id"],
            "symbols":        set(json.loads(r["symbols"])),
            "patterns":       set(json.loads(r["patterns"])),
            "timeframes":     set(json.loads(r["timeframes"])),
            "entry_models":   set(json.loads(r["entry_models"] or json.dumps(DEFAULT_ENTRY_MODELS))),
            "trade_directions": set(json.loads(r["trade_directions"] or json.dumps(DEFAULT_TRADE_DIRECTIONS))),
            "charts_enabled": bool(r["charts_enabled"]) if r["charts_enabled"] is not None else False,
        })
    return result


def set_active(user_id: int, active: bool):
    upsert_user(user_id, active=int(active))


def save_preferences(
    user_id: int,
    symbols: set,
    patterns: set,
    timeframes: set,
    entry_models: set | None = None,
    trade_directions: set | None = None,
):
    upsert_user(
        user_id,
        symbols=list(symbols),
        patterns=list(patterns),
        timeframes=list(timeframes),
        entry_models=list(entry_models or DEFAULT_ENTRY_MODELS),
        trade_directions=list(trade_directions or DEFAULT_TRADE_DIRECTIONS),
        active=1,
        setup_done=1,
    )


def set_subscription(user_id: int, days: int):
    """Activate subscription for N days from now."""
    from datetime import datetime, timezone, timedelta
    expires = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    upsert_user(user_id, expires_at=expires)


def is_subscribed(user_id: int) -> bool:
    """Check if user has active subscription (or is owner)."""
    from datetime import datetime, timezone
    user = get_user(user_id)
    if not user:
        return False
    if user.get("is_owner"):
        return True
    expires = user.get("expires_at")
    if not expires:
        return False
    try:
        exp_dt = datetime.fromisoformat(expires)
        return datetime.now(timezone.utc) < exp_dt
    except Exception:
        return False


def set_owner(user_id: int):
    """Grant permanent free access."""
    upsert_user(user_id, is_owner=1)


def get_subscription_status(user_id: int) -> str:
    """Human-readable subscription status string."""
    from datetime import datetime, timezone
    import math
    user = get_user(user_id)
    if not user:
        return "No subscription"
    if user.get("is_owner"):
        return "👑 Owner — lifetime access"
    expires = user.get("expires_at")
    if not expires:
        return "No active subscription"
    try:
        exp_dt = datetime.fromisoformat(expires)
        now    = datetime.now(timezone.utc)
        if now >= exp_dt:
            return "❌ Subscription expired"
        days_left = max(1, math.ceil((exp_dt - now).total_seconds() / 86400))
        return f"✅ Active — {days_left} days remaining"
    except Exception:
        return "Unknown"


def get_session_alert_users() -> list[int]:
    """Return user_ids of all active subscribed users with sessions_alerts enabled."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE active=1 AND setup_done=1 AND sessions_alerts=1"
        ).fetchall()
    return [r["user_id"] for r in rows if _has_live_access_row(r)]


def toggle_sessions_alerts(user_id: int) -> bool:
    """Toggle sessions_alerts for user. Returns new state."""
    user = get_user(user_id)
    new_val = not user.get("sessions_alerts", False) if user else True
    upsert_user(user_id, sessions_alerts=int(new_val))
    return new_val


def toggle_charts(user_id: int) -> bool:
    """Toggle auto chart generation. Returns new state."""
    user    = get_user(user_id)
    new_val = not user.get("charts_enabled", False) if user else True
    upsert_user(user_id, charts_enabled=int(new_val))
    return new_val
