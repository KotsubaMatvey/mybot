from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from market_primitives.common import fmt_price

from .types import AlertPayload


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def build_alert_message(symbol: str, timeframe: str, alerts: Iterable[AlertPayload]) -> str:
    payloads = list(alerts)
    if payloads and all(item.alert_kind == "strategy" for item in payloads):
        return "\n\n".join(build_strategy_alert_text(item) for item in payloads)

    lines = [f"{symbol}  {timeframe}"]
    lines.extend(f"- {alert.detail}" for alert in payloads)
    return "\n".join(lines)


def build_strategy_alert_text(alert: AlertPayload) -> str:
    lines = []
    if alert.context_timeframe:
        lines.append(f"{alert.symbol}  HTF {alert.context_timeframe} / LTF {alert.timeframe}")
    else:
        lines.append(f"{alert.symbol}  {alert.timeframe}")
    lines.append(f"{alert.pattern}  {(alert.trade_direction or '').upper()}")
    htf_bias = alert.metadata.get("htf_bias")
    if htf_bias and htf_bias != "none":
        htf_location = alert.metadata.get("htf_location", "unknown")
        htf_zone = alert.metadata.get("htf_zone_type", "None")
        htf_objective = alert.metadata.get("htf_objective_type", "none")
        lines.append(f"HTF: {alert.context_timeframe or '-'} {htf_bias} {htf_location} {htf_zone} objective {htf_objective}")
    if alert.status:
        lines.append(f"Status: {alert.status.upper()}")
    if alert.reason:
        lines.append(alert.reason)
    if alert.entry_low is not None and alert.entry_high is not None:
        lines.append(f"Entry zone: {fmt_price(alert.entry_low)} - {fmt_price(alert.entry_high)}")
    if alert.invalidation is not None:
        lines.append(f"Invalidation: {fmt_price(alert.invalidation)}")
    if alert.score is not None:
        lines.append(f"Score: {alert.score}/5")
    return "\n".join(lines)


def build_chart_caption(symbol: str, timeframe: str, alerts: Iterable[AlertPayload]) -> str:
    payloads = list(alerts)
    if not payloads:
        return f"{symbol}  {timeframe}"
    strategy = next((alert for alert in payloads if alert.alert_kind == "strategy"), None)
    if strategy is not None:
        parts = [f"{symbol}  {timeframe}", f"{strategy.pattern} {str(strategy.trade_direction or '').upper()}"]
        if strategy.score is not None:
            parts.append(f"{strategy.score}/5")
        return " | ".join(part for part in parts if part)
    patterns = ", ".join(alert.pattern for alert in payloads[:3])
    return f"{symbol}  {timeframe} | {patterns}"


def build_payment_message(price: str | float, expired: bool = False) -> str:
    expired_line = "\nYour subscription has expired.\n" if expired else ""
    return (
        "Subscribe to ICT Crypto Alerts\n"
        f"{expired_line}\n"
        f"Price: `${price}` / month\n"
        "Pay in any crypto - USDT | TON | BTC | ETH\n\n"
        "Includes:\n"
        "- Real-time ICT pattern detection\n"
        "- Entry Model 1 / 2 / 3 alerts\n"
        "- Primitive FVG | IFVG | OB | BOS | CHoCH alerts\n"
        "- Multi-timeframe zone tracking\n"
        "After payment tap Check Payment below."
    )


def build_dashboard_message(user: dict, zone_count: int, alerts_today: int, sub_status: str) -> str:
    status = "Active" if user["active"] else "Paused"
    symbols = " | ".join(sorted(user["symbols"]))
    timeframes = " | ".join(sorted(user["timeframes"]))
    models = " | ".join(sorted(user.get("entry_models", [])))
    directions = set(user.get("trade_directions", []))
    direction_text = "Both" if directions == {"long", "short"} else " | ".join(sorted(item.upper() for item in directions))
    return (
        "ICT Crypto Alerts\n\n"
        f"Status: {status}\n"
        f"Pairs: {symbols}\n"
        f"Timeframes: {timeframes}\n"
        f"Entry Models: {models}\n"
        f"Directions: {direction_text}\n"
        f"Subscription: {sub_status}\n\n"
        f"Last scan: {utc_now()}\n"
        f"Active zones: {zone_count}\n"
        f"Alerts today: {alerts_today}"
    )


def build_setup_summary(symbols, patterns, timeframes, entry_models, trade_directions) -> str:
    symbols_text = ", ".join(sorted(symbols))
    patterns_text = ", ".join(sorted(patterns))
    timeframes_text = ", ".join(sorted(timeframes))
    models_text = ", ".join(sorted(entry_models))
    directions = set(trade_directions)
    direction_text = "Both" if directions == {"long", "short"} else ", ".join(sorted(item.upper() for item in directions))
    return (
        f"Preferences set: {symbols_text} - {patterns_text} - {timeframes_text}\n"
        f"Entry models: {models_text}\n"
        f"Directions: {direction_text}\n\n"
        "Alerts will arrive automatically."
    )


__all__ = [
    "build_alert_message",
    "build_chart_caption",
    "build_dashboard_message",
    "build_payment_message",
    "build_setup_summary",
    "build_strategy_alert_text",
    "utc_now",
]
