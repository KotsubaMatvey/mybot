"""
alerts.py — scanner loop, signal dispatch, digest
"""
import asyncio
import logging
from datetime import datetime, timezone

from telegram.ext import Application

from scanner import run_scanner, get_active_zones
from database import get_all_active_users, is_subscribed
from interpret import pattern_to_interpretation
from formatters import build_alert_message, utc_now, score_label
from config import SCAN_INTERVAL, DIGEST_INTERVAL, TIMEFRAMES
from health import record_scan, record_alert, record_error

logger = logging.getLogger(__name__)

# Shared state — imported by bot.py for /status command
signals_today: dict = {}


async def scanner_loop(application: Application):
    logger.info("Scanner loop started")
    last_digest = 0

    while True:
        try:
            alerts, confluences, all_candles = await run_scanner()
            record_scan()
            users = get_all_active_users()
            now   = asyncio.get_event_loop().time()

            # Group alerts by (symbol, tf)
            grouped_meta: dict = {}
            scores: dict       = {}
            for a in alerts:
                key = (a["symbol"], a["timeframe"])
                grouped_meta.setdefault(key, []).append(a)
                scores[key] = a.get("score", 0)

            for user in users:
                uid = user["user_id"]
                if not is_subscribed(uid):
                    continue

                for (symbol, tf), meta_list in grouped_meta.items():
                    if symbol not in user["symbols"] or tf not in user["timeframes"]:
                        continue
                    filtered = [m for m in meta_list if m["pattern"] in user["patterns"]]
                    if not filtered:
                        continue
                    score = scores.get((symbol, tf), 0)
                    try:
                        msg = build_alert_message(symbol, tf, filtered, score)
                        await application.bot.send_message(uid, msg, parse_mode="Markdown")
                        signals_today[uid] = signals_today.get(uid, 0) + 1
                        record_alert()
                    except Exception as e:
                        logger.error(f"Alert send error {uid}: {e}")
                        record_error()

                # Interpretations (confluence)
                if user.get("confluence", True):
                    sent_interp = set()
                    for (symbol, tf), meta_list in grouped_meta.items():
                        if symbol not in user["symbols"] or tf not in user["timeframes"]:
                            continue
                        if (symbol, tf) in sent_interp:
                            continue
                        filtered = [m for m in meta_list if m["pattern"] in user["patterns"]]
                        if not filtered:
                            continue
                        candles = all_candles.get((symbol, tf), [])
                        interp  = pattern_to_interpretation(filtered, candles, symbol, tf)
                        if interp:
                            try:
                                await application.bot.send_message(uid, interp, parse_mode="Markdown")
                                sent_interp.add((symbol, tf))
                            except Exception as e:
                                logger.error(f"Interp send error {uid}: {e}")

            # Hourly digest
            if now - last_digest >= DIGEST_INTERVAL:
                last_digest = now
                if datetime.now(timezone.utc).hour == 0:
                    signals_today.clear()
                await _send_digest(application, users)

        except Exception as e:
            logger.error(f"Scanner loop error: {e}")
            record_error()

        await asyncio.sleep(SCAN_INTERVAL)


async def _send_digest(application: Application, users: list):
    zones = get_active_zones()
    if not zones:
        return
    for user in users:
        uid = user["user_id"]
        if not is_subscribed(uid):
            continue
        lines = [f"📋 *Hourly Digest  ·  {utc_now()}*"]
        has   = False
        for symbol in sorted(user["symbols"]):
            sym_lines = [f"\n*{symbol}*"]
            for tf in TIMEFRAMES:
                if tf not in user["timeframes"]:
                    continue
                for p in zones.get(symbol, {}).get(tf, []):
                    if p["type"] in user["patterns"]:
                        sym_lines.append(f"  `{tf}`  {p['detail']}")
                        has = True
            if len(sym_lines) > 1:
                lines.extend(sym_lines)
        if has:
            lines += ["", f"_Signals today: {signals_today.get(uid, 0)}_"]
            try:
                await application.bot.send_message(uid, "\n".join(lines), parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Digest error {uid}: {e}")
