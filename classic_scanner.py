"""Classic TA channel alert orchestration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from classic_fetcher import fetch_candles, fetch_cme_close, fetch_orderbook
from classic_formatters import fmt_bounce, fmt_cme, fmt_pattern, fmt_rsi, fmt_setup
from classic_indicators import analyze_ob, calc_rsi, compute_sl_tp, detect_pattern, rsi_is_extreme, rsi_state

logger = logging.getLogger(__name__)

CHANNEL_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
SCAN_TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]
TF_SECONDS = {
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}
_posted: dict[tuple, bool] = {}


def _seconds_until_close(timeframe: str) -> float:
    period = TF_SECONDS.get(timeframe, 60)
    now = datetime.now(timezone.utc).timestamp()
    last = (int(now) // period) * period
    return max(last + period - now, 0)


def _candle_key(timeframe: str) -> int:
    period = TF_SECONDS.get(timeframe, 60)
    now = int(datetime.now(timezone.utc).timestamp())
    return (now // period) * period


async def _analyze(symbol: str, timeframe: str) -> dict:
    candles = await fetch_candles(symbol, timeframe, limit=100)
    if not candles:
        return {}

    price = candles[-1]["close"]
    rsi = calc_rsi(candles)
    if rsi is None:
        return {}

    rsi_label, rsi_direction = rsi_state(rsi)
    pattern = detect_pattern(candles)
    orderbook_raw = await fetch_orderbook(symbol)
    orderbook = analyze_ob(orderbook_raw, price)

    return {
        "symbol": symbol,
        "tf": timeframe,
        "price": price,
        "candles": candles,
        "rsi": rsi,
        "rsi_label": rsi_label,
        "rsi_direction": rsi_direction,
        "extreme": rsi_is_extreme(rsi),
        "pattern": pattern,
        "orderbook": orderbook,
        "orderbook_dominant": orderbook.get("dominant", "neutral"),
    }


def _build_messages(data: dict) -> list[dict[str, str]]:
    if not data:
        return []

    symbol = data["symbol"]
    timeframe = data["tf"]
    price = data["price"]
    candles = data["candles"]
    rsi_direction = data["rsi_direction"]
    extreme = data["extreme"]
    pattern = data["pattern"]
    orderbook = data["orderbook"]
    orderbook_dominant = data["orderbook_dominant"]
    messages: list[dict[str, str]] = []
    directional_pattern = bool(pattern and pattern[1] != "neutral")

    if directional_pattern:
        pattern_name, pattern_direction = pattern
        orderbook_confirms = (
            (orderbook_dominant == "bids" and pattern_direction == "bullish")
            or (orderbook_dominant == "asks" and pattern_direction == "bearish")
        )
        rsi_confirms = (
            (rsi_direction == "bullish" and pattern_direction == "bullish")
            or (rsi_direction == "bearish" and pattern_direction == "bearish")
        )
        if orderbook_confirms or rsi_confirms:
            messages.append(
                {
                    "type": "pattern",
                    "msg": fmt_pattern(symbol, timeframe, pattern_name, pattern_direction, price, orderbook),
                }
            )
            if timeframe in {"1h", "4h", "1d"}:
                bullish = sum(
                    [
                        rsi_direction == "bullish",
                        orderbook_dominant == "bids",
                        pattern_direction == "bullish",
                    ]
                )
                bearish = sum(
                    [
                        rsi_direction == "bearish",
                        orderbook_dominant == "asks",
                        pattern_direction == "bearish",
                    ]
                )
                if bullish == 3 or bearish == 3:
                    direction = "bullish" if bullish == 3 else "bearish"
                    trade_type = ("Scalp" if timeframe == "1h" else "Trend") + (" Long" if direction == "bullish" else " Short")
                    stop_loss, tp1, tp2, tp3 = compute_sl_tp(candles, direction, price)
                    messages.append(
                        {
                            "type": "setup",
                            "msg": fmt_setup(symbol, timeframe, trade_type, price, stop_loss, tp1, tp2, tp3, orderbook),
                        }
                    )
    elif extreme:
        if (rsi_direction == "bullish" and orderbook_dominant == "bids") or (
            rsi_direction == "bearish" and orderbook_dominant == "asks"
        ):
            messages.append({"type": "bounce", "msg": fmt_bounce(symbol, timeframe, rsi_direction)})

    return messages


async def _post(bot, channel_id: str, message: str, key: tuple) -> None:
    if _posted.get(key):
        return
    try:
        await bot.send_message(channel_id, message, parse_mode="Markdown")
        _posted[key] = True
        await asyncio.sleep(0.5)
    except Exception as exc:
        logger.error("Post error %s: %s", key, exc)


def _trim_posted() -> None:
    if len(_posted) <= 2000:
        return
    for key in list(_posted)[:500]:
        del _posted[key]


async def _watch_tf(bot, channel_id: str, timeframe: str) -> None:
    while True:
        await asyncio.sleep(_seconds_until_close(timeframe) + 2)
        candle_key = _candle_key(timeframe)
        rsi_groups: dict[str, list[str]] = {}
        symbol_messages: dict[str, list[dict[str, str]]] = {}

        for symbol in CHANNEL_SYMBOLS:
            try:
                result = await _analyze(symbol, timeframe)
                symbol_messages[symbol] = _build_messages(result)
                if result.get("extreme"):
                    label = result["rsi_label"]
                    rsi_groups.setdefault(label, []).append(symbol)
                await asyncio.sleep(0.3)
            except Exception as exc:
                logger.error("Analyze error %s %s: %s", symbol, timeframe, exc)

        for label, symbols in rsi_groups.items():
            await _post(bot, channel_id, fmt_rsi(timeframe, label, symbols), ("rsi", timeframe, candle_key, label))

        for symbol, messages in symbol_messages.items():
            for item in messages:
                await _post(bot, channel_id, item["msg"], (item["type"], symbol, timeframe, candle_key))

        if timeframe == "15m":
            now = datetime.now(timezone.utc)
            if now.weekday() == 0 and now.hour == 0 and 10 <= now.minute <= 12:
                cme_key = ("cme", now.date().isoformat())
                if not _posted.get(cme_key):
                    price = await fetch_cme_close()
                    if price:
                        await _post(bot, channel_id, fmt_cme(price), cme_key)

        _trim_posted()


async def channel_scheduler(bot, channel_id: str) -> None:
    logger.info(
        "Channel scheduler started | timeframes=%s | symbols=%s",
        len(SCAN_TIMEFRAMES),
        len(CHANNEL_SYMBOLS),
    )
    await asyncio.gather(*[_watch_tf(bot, channel_id, timeframe) for timeframe in SCAN_TIMEFRAMES])


__all__ = ["channel_scheduler"]
