from __future__ import annotations

from database import get_subscription_status, get_user, is_subscribed
from formatters import build_dashboard_message
from scanner import get_active_zones


def user_ready(user: dict | None) -> bool:
    if not user:
        return False
    return bool(
        user.get("setup_done")
        and user.get("symbols")
        and user.get("patterns")
        and user.get("timeframes")
        and user.get("entry_models")
        and user.get("trade_directions")
    )


def alert_enabled_for_user(alert, user: dict) -> bool:
    if getattr(alert, "alert_kind", None) == "strategy":
        return (
            alert.pattern in user.get("entry_models", set())
            and (alert.trade_direction or "") in user.get("trade_directions", set())
        )
    return alert.pattern in user.get("patterns", set())


def filter_cached_alerts(patterns, user: dict | None):
    if not user:
        return []
    return [pattern for pattern in patterns if alert_enabled_for_user(pattern, user)]


async def send_dashboard(user_id: int, context, update=None) -> None:
    user = get_user(user_id)
    if not user:
        return
    zones = get_active_zones()
    from alerts import signals_today
    from keyboards import main_menu

    today = signals_today.get(user_id, 0)
    sub_status = get_subscription_status(user_id)
    zone_count = sum(
        1
        for symbol in user["symbols"]
        for timeframe, alerts in zones.get(symbol, {}).items()
        if timeframe in user["timeframes"]
        for alert in alerts
        if alert_enabled_for_user(alert, user)
    )
    text = build_dashboard_message(user, zone_count, today, sub_status)
    if update:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await context.bot.send_message(user_id, text, reply_markup=main_menu())


__all__ = [
    "alert_enabled_for_user",
    "filter_cached_alerts",
    "is_subscribed",
    "send_dashboard",
    "user_ready",
]
