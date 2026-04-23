"""Formatting helpers for Telegram messages."""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def fmt_price(price: float) -> str:
    if price >= 1000:
        return f"{price:,.1f}"
    if price >= 1:
        return f"{price:.2f}"
    return f"{price:.4f}"


def build_alert_message(symbol: str, timeframe: str, patterns_meta: list) -> str:
    if patterns_meta and all(item.get("alert_kind") == "strategy" for item in patterns_meta):
        return "\n\n".join(item.get("detail", "") for item in patterns_meta if item.get("detail"))

    lines = [f"{symbol}  ·  {timeframe}"]
    for pattern in patterns_meta:
        detail = pattern.get("detail", "")
        lines.append(f"- {detail}")
    return "\n".join(lines)


def build_payment_message(price, expired: bool = False) -> str:
    expired_line = "\nYour subscription has expired.\n" if expired else ""
    return (
        f"Subscribe to ICT Crypto Alerts\n"
        f"{expired_line}\n"
        f"Price: `${price}` / month\n"
        f"Pay in any crypto - USDT · TON · BTC · ETH\n\n"
        f"Includes:\n"
        f"- Real-time ICT pattern detection\n"
        f"- Entry Model 1 / 2 / 3 alerts\n"
        f"- Primitive FVG · IFVG · OB · BOS · CHoCH alerts\n"
        f"- Multi-timeframe zone tracking\n"
        f"After payment tap Check Payment below."
    )


def build_dashboard_message(user: dict, zone_count: int, alerts_today: int, sub_status: str) -> str:
    status = "Active" if user["active"] else "Paused"
    syms_str = " | ".join(sorted(user["symbols"]))
    tfs_str = " | ".join(sorted(user["timeframes"]))
    models_str = " | ".join(sorted(user.get("entry_models", [])))
    directions = set(user.get("trade_directions", []))
    dirs_str = "Both" if directions == {"long", "short"} else " | ".join(sorted(direction.upper() for direction in directions))
    return (
        f"ICT Crypto Alerts\n\n"
        f"Status: {status}\n"
        f"Pairs: {syms_str}\n"
        f"Timeframes: {tfs_str}\n"
        f"Entry Models: {models_str}\n"
        f"Directions: {dirs_str}\n"
        f"Subscription: {sub_status}\n\n"
        f"Last scan: {utc_now()}\n"
        f"Active zones: {zone_count}\n"
        f"Alerts today: {alerts_today}"
    )


def build_setup_summary(symbols, patterns, timeframes, entry_models, trade_directions) -> str:
    syms = ", ".join(sorted(symbols))
    pats = ", ".join(sorted(patterns))
    tfs = ", ".join(sorted(timeframes))
    models = ", ".join(sorted(entry_models))
    directions = set(trade_directions)
    dirs = "Both" if directions == {"long", "short"} else ", ".join(sorted(direction.upper() for direction in directions))
    return (
        f"Preferences set: {syms} - {pats} - {tfs}\n"
        f"Entry models: {models}\n"
        f"Directions: {dirs}\n\n"
        f"Alerts will arrive automatically."
    )
