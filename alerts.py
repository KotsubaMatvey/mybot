"""Scanner loop and Telegram signal dispatch."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

from config import DIGEST_INTERVAL, SCAN_INTERVAL, TIMEFRAMES
from database import get_all_active_users
from formatters import build_alert_message, utc_now
from health import record_alert, record_error, record_scan
from presentation.types import AlertPayload
from scanner import get_active_zones, run_scanner
from visuals import generate_chart

logger = logging.getLogger(__name__)

signals_today: dict[int, int] = {}
_last_reset_date = None


def _chart_button(symbol: str, timeframe: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Chart", callback_data=f"chart_{symbol}_{timeframe}")]]
    )


def _alert_enabled_for_user(alert: AlertPayload, user: dict) -> bool:
    if alert.alert_kind == "strategy":
        return (
            alert.pattern in user.get("entry_models", set())
            and (alert.trade_direction or "") in user.get("trade_directions", set())
        )
    return alert.pattern in user.get("patterns", set())


async def scanner_loop(application: Application) -> None:
    global _last_reset_date
    logger.info("Scanner loop started")
    last_digest = 0.0

    while True:
        try:
            alerts, _, all_candles = await run_scanner()
            record_scan()
            users = get_all_active_users()
            now = asyncio.get_event_loop().time()

            today = datetime.now(timezone.utc).date()
            if today != _last_reset_date:
                signals_today.clear()
                _last_reset_date = today

            grouped: dict[tuple[str, str], list[AlertPayload]] = {}
            for alert in alerts:
                grouped.setdefault((alert.symbol, alert.timeframe), []).append(alert)

            for user in users:
                user_id = user["user_id"]
                auto_charts = user.get("charts_enabled", False)
                for (symbol, timeframe), grouped_alerts in grouped.items():
                    if symbol not in user["symbols"] or timeframe not in user["timeframes"]:
                        continue
                    filtered = [alert for alert in grouped_alerts if _alert_enabled_for_user(alert, user)]
                    if not filtered:
                        continue

                    batches = [
                        [item for item in filtered if item.alert_kind == "strategy"],
                        [item for item in filtered if item.alert_kind == "primitive"],
                    ]
                    for batch in batches:
                        if not batch:
                            continue
                        try:
                            message = build_alert_message(symbol, timeframe, batch)
                            candles = all_candles.get((symbol, timeframe), [])
                            if auto_charts and candles:
                                chart = await generate_chart(candles, batch, symbol, timeframe)
                                if chart is not None:
                                    await application.bot.send_photo(
                                        user_id,
                                        photo=chart,
                                        caption=message,
                                        reply_markup=_chart_button(symbol, timeframe),
                                    )
                                else:
                                    await application.bot.send_message(
                                        user_id,
                                        message,
                                        reply_markup=_chart_button(symbol, timeframe),
                                    )
                            else:
                                await application.bot.send_message(
                                    user_id,
                                    message,
                                    reply_markup=_chart_button(symbol, timeframe),
                                )
                            signals_today[user_id] = signals_today.get(user_id, 0) + 1
                            record_alert()
                            await asyncio.sleep(0.05)
                        except Exception as exc:
                            logger.error("Alert send error %s: %s", user_id, exc)
                            record_error()

            if now - last_digest >= DIGEST_INTERVAL:
                last_digest = now
                await _send_digest(application, users)

        except Exception as exc:
            logger.error("Scanner loop error: %s", exc, exc_info=True)
            record_error()

        await asyncio.sleep(SCAN_INTERVAL)


async def _send_digest(application: Application, users: list[dict]) -> None:
    zones = get_active_zones()
    if not zones:
        return
    for user in users:
        user_id = user["user_id"]
        lines = [f"Hourly Digest | {utc_now()}"]
        has_alerts = False
        for symbol in sorted(user["symbols"]):
            symbol_lines = [f"\n{symbol}"]
            for timeframe in TIMEFRAMES:
                if timeframe not in user["timeframes"]:
                    continue
                for alert in zones.get(symbol, {}).get(timeframe, []):
                    if _alert_enabled_for_user(alert, user):
                        symbol_lines.append(f"  {timeframe}  {alert.detail}")
                        has_alerts = True
            if len(symbol_lines) > 1:
                lines.extend(symbol_lines)
        if not has_alerts:
            continue
        lines += ["", f"Signals today: {signals_today.get(user_id, 0)}"]
        try:
            await application.bot.send_message(user_id, "\n".join(lines))
        except Exception as exc:
            logger.error("Digest error %s: %s", user_id, exc)


__all__ = ["scanner_loop", "signals_today"]
