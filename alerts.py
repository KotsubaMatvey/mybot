"""Scanner loop and Telegram signal dispatch."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from telegram.ext import Application

from config import DIGEST_INTERVAL, SCAN_INTERVAL, TIMEFRAMES
from database import get_all_active_users
from formatters import build_alert_message, utc_now
from health import record_alert, record_error, record_scan
from scanner import get_active_zones, run_scanner
from visuals import generate_chart

logger = logging.getLogger(__name__)


def _chart_button(symbol: str, tf: str):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Chart", callback_data=f"chart_{symbol}_{tf}")]]
    )


signals_today: dict = {}
_last_reset_date = None


def _alert_enabled_for_user(alert: dict, user: dict) -> bool:
    if alert.get("alert_kind") == "strategy":
        setup = alert.get("setup")
        direction = getattr(setup, "direction", None) if setup else None
        return (
            alert.get("pattern") in user.get("entry_models", set())
            and direction in user.get("trade_directions", set())
        )
    return alert.get("pattern") in user.get("patterns", set())


async def scanner_loop(application: Application):
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

            grouped: dict[tuple[str, str], list[dict]] = {}
            for alert in alerts:
                key = (alert["symbol"], alert["timeframe"])
                grouped.setdefault(key, []).append(alert)

            for user in users:
                uid = user["user_id"]
                auto_charts = user.get("charts_enabled", False)
                for (symbol, tf), meta_list in grouped.items():
                    if symbol not in user["symbols"] or tf not in user["timeframes"]:
                        continue
                    filtered = [meta for meta in meta_list if _alert_enabled_for_user(meta, user)]
                    if not filtered:
                        continue
                    batches = [
                        [item for item in filtered if item.get("alert_kind") == "strategy"],
                        [item for item in filtered if item.get("alert_kind") != "strategy"],
                    ]
                    for batch in batches:
                        if not batch:
                            continue
                        try:
                            msg = build_alert_message(symbol, tf, batch)
                            candles = all_candles.get((symbol, tf), [])
                            if auto_charts and candles:
                                chart = await generate_chart(candles, batch, symbol, tf)
                                if chart:
                                    await application.bot.send_photo(
                                        uid,
                                        photo=chart,
                                        caption=msg,
                                        reply_markup=_chart_button(symbol, tf),
                                    )
                                else:
                                    await application.bot.send_message(uid, msg, reply_markup=_chart_button(symbol, tf))
                            else:
                                await application.bot.send_message(uid, msg, reply_markup=_chart_button(symbol, tf))
                            signals_today[uid] = signals_today.get(uid, 0) + 1
                            record_alert()
                            await asyncio.sleep(0.05)
                        except Exception as exc:
                            logger.error("Alert send error %s: %s", uid, exc)
                            record_error()

            if now - last_digest >= DIGEST_INTERVAL:
                last_digest = now
                await _send_digest(application, users)

        except Exception as exc:
            logger.error("Scanner loop error: %s", exc)
            record_error()

        await asyncio.sleep(SCAN_INTERVAL)


async def _send_digest(application: Application, users: list):
    zones = get_active_zones()
    if not zones:
        return
    for user in users:
        uid = user["user_id"]
        lines = [f"Hourly Digest · {utc_now()}"]
        has = False
        for symbol in sorted(user["symbols"]):
            symbol_lines = [f"\n{symbol}"]
            for tf in TIMEFRAMES:
                if tf not in user["timeframes"]:
                    continue
                for pattern in zones.get(symbol, {}).get(tf, []):
                    if _alert_enabled_for_user(pattern, user):
                        symbol_lines.append(f"  {tf}  {pattern['detail']}")
                        has = True
            if len(symbol_lines) > 1:
                lines.extend(symbol_lines)
        if has:
            lines += ["", f"Signals today: {signals_today.get(uid, 0)}"]
            try:
                await application.bot.send_message(uid, "\n".join(lines))
            except Exception as exc:
                logger.error("Digest error %s: %s", uid, exc)
