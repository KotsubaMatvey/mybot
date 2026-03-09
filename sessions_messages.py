"""
sessions_messages.py — message builders for session alerts.
Pure functions — no I/O, no async.
"""
from datetime import datetime, timezone


# ── Session definitions — used for /session query
SESSIONS = {
    "Asia":   (0,  9),
    "London": (8,  17),
    "NY":     (13, 22),
}

SESSION_EMOJI = {
    "Asia":   "🌏",
    "London": "🌍",
    "NY":     "🗽",
}

# ── Event schedule: (hour, minute, event_key)
EVENTS: list[tuple[int, int, str]] = [
    (0,  0,  "asia_open"),
    (8,  0,  "london_open"),
    (9,  0,  "asia_close"),
    (13, 0,  "ny_open"),
    (17, 0,  "london_close"),
    (22, 0,  "ny_close"),
]


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def _fmt(p: float) -> str:
    return f"{p:,.1f}" if p >= 1000 else f"{p:.2f}"


def _range_line(asian_range: tuple[float, float] | None) -> str:
    if not asian_range:
        return ""
    hi, lo = asian_range
    return f"\nAsian Range:  `{_fmt(lo)} — {_fmt(hi)}`"


# ── Individual builders

def build_open(name: str, asian_range: tuple | None = None) -> str:
    emoji = SESSION_EMOJI[name]
    lines = [f"{emoji} *{name} Open*  ·  {_ts()}"]
    rng   = _range_line(asian_range)
    if rng:
        lines.append(rng)
    return "\n".join(lines)


def build_close(name: str) -> str:
    emoji = SESSION_EMOJI[name]
    return f"{emoji} *{name} Close*  ·  {_ts()}"


def build_overlap_start() -> str:
    return f"⚡ *London + NY Overlap started*  ·  {_ts()}\n_Most active period of the day_"


def build_overlap_end() -> str:
    return f"🔔 *London + NY Overlap ended*  ·  {_ts()}"


# ── Event → message

def build_event_message(event_key: str, asian_range: tuple | None = None) -> str | None:
    match event_key:
        case "asia_open":
            return build_open("Asia")
        case "asia_close":
            return build_close("Asia")
        case "london_open":
            return build_open("London", asian_range)
        case "london_close":
            return build_overlap_end() + "\n\n" + build_close("London")
        case "ny_open":
            return build_open("NY", asian_range) + "\n\n" + build_overlap_start()
        case "ny_close":
            return build_close("NY")
    return None


# ── Current session status (for /session command)

def build_current_session() -> str:
    now_h  = datetime.now(timezone.utc).hour
    active = [name for name, (start, end) in SESSIONS.items()
              if start <= now_h < end]

    if not active:
        return f"🌙 *No major session active*  ·  {_ts()}\n_Pre-Asia_"

    if len(active) == 2:
        names = " + ".join(active)
        return f"⚡ *{names} Overlap*  ·  {_ts()}\n_Most active period_"

    name = active[0]
    return f"{SESSION_EMOJI[name]} *{name} Session active*  ·  {_ts()}"
