"""
classic_scanner.py — orchestrates channel alerts for Trillion Strategy.

Composes: classic_fetcher + classic_indicators + classic_formatters.
This file contains only flow logic — no HTTP, no formatting, no math.

Message types:
  1. RSI alert     — grouped by symbol, fires on extreme RSI
  2. Pattern alert — Pinbar/Predict + OB confirmation, no entry/SL
  3. Setup         — Scalp/Trend Long/Short, only 1h/4h/1d, all 3 signals agree
  4. Bounce        — RSI extreme + OB confirm, no candle pattern
  5. CME close     — Monday 00:10 UTC
"""
import asyncio
import logging
from datetime import datetime, timezone

from classic_fetcher    import fetch_candles, fetch_orderbook, fetch_cme_close
from classic_indicators import (
    calc_rsi, rsi_state, rsi_is_extreme,
    detect_pattern, analyze_ob, compute_sl_tp,
)
from classic_formatters import (
    fmt_rsi, fmt_pattern, fmt_setup, fmt_bounce, fmt_cme,
)

logger = logging.getLogger(__name__)

CHANNEL_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
SCAN_TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]

TF_SECONDS = {
    "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400, "1d": 86400,
}

# Dedup: tuple key → True
_posted: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  TIMING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _seconds_until_close(tf: str) -> float:
    period = TF_SECONDS.get(tf, 60)
    now    = datetime.now(timezone.utc).timestamp()
    last   = (int(now) // period) * period
    return max(last + period - now, 0)


def _candle_key(tf: str) -> int:
    period = TF_SECONDS.get(tf, 60)
    now    = int(datetime.now(timezone.utc).timestamp())
    return (now // period) * period


# ══════════════════════════════════════════════════════════════════════════════
#  SIGNAL ANALYSIS — one symbol + tf
# ══════════════════════════════════════════════════════════════════════════════

async def _analyze(symbol: str, tf: str) -> dict:
    """
    Fetch data and compute all signals for one symbol+tf.
    Returns structured result — no formatting here.
    """
    candles = await fetch_candles(symbol, tf, limit=100)
    if not candles:
        return {}

    price = candles[-1]["close"]
    rsi   = calc_rsi(candles)
    if rsi is None:
        return {}

    rsi_lbl, rsi_dir = rsi_state(rsi)
    extreme          = rsi_is_extreme(rsi)
    pattern          = detect_pattern(candles)

    ob_raw  = await fetch_orderbook(symbol)
    ob      = analyze_ob(ob_raw, price)
    ob_dom  = ob.get("dominant", "neutral")

    return {
        "symbol":   symbol,
        "tf":       tf,
        "price":    price,
        "candles":  candles,
        "rsi":      rsi,
        "rsi_lbl":  rsi_lbl,
        "rsi_dir":  rsi_dir,
        "extreme":  extreme,
        "pattern":  pattern,
        "ob":       ob,
        "ob_dom":   ob_dom,
    }


def _build_messages(d: dict) -> list[dict]:
    """
    Decide which message types to generate from analysis result.
    Returns list of {"type": str, "msg": str}.
    All formatting delegated to classic_formatters.
    """
    if not d:
        return []

    symbol  = d["symbol"]
    tf      = d["tf"]
    price   = d["price"]
    candles = d["candles"]
    rsi_dir = d["rsi_dir"]
    extreme = d["extreme"]
    pattern = d["pattern"]
    ob      = d["ob"]
    ob_dom  = d["ob_dom"]
    messages = []

    # ── Type 2 + 3: Pattern detected
    if pattern and pattern[1] != "neutral":
        pat_name, pat_dir = pattern

        ob_confirms  = (ob_dom == "bids"  and pat_dir == "bullish") or \
                       (ob_dom == "asks"  and pat_dir == "bearish")
        rsi_confirms = (rsi_dir == "bullish" and pat_dir == "bullish") or \
                       (rsi_dir == "bearish" and pat_dir == "bearish")

        if ob_confirms or rsi_confirms:
            # Type 2: pattern message
            messages.append({
                "type": "pattern",
                "msg":  fmt_pattern(symbol, tf, pat_name, pat_dir, price, ob),
            })

            # Type 3: full setup — only higher TFs, all 3 signals must agree
            if tf in ("1h", "4h", "1d"):
                bull = sum([rsi_dir == "bullish", ob_dom == "bids", pat_dir == "bullish"])
                bear = sum([rsi_dir == "bearish", ob_dom == "asks", pat_dir == "bearish"])
                if bull == 3 or bear == 3:
                    direction  = "bullish" if bull == 3 else "bearish"
                    trade_type = (
                        ("Scalp" if tf == "1h" else "Trend") +
                        (" Long" if direction == "bullish" else " Short")
                    )
                    sl, tp1, tp2, tp3 = compute_sl_tp(candles, direction, price)
                    messages.append({
                        "type": "setup",
                        "msg":  fmt_setup(symbol, tf, trade_type, price, sl, tp1, tp2, tp3, ob),
                    })

    # ── Type 4: Bounce — RSI extreme + OB, no candle pattern
    elif extreme and not pattern:
        if (rsi_dir == "bullish" and ob_dom == "bids") or \
           (rsi_dir == "bearish" and ob_dom == "asks"):
            messages.append({
                "type": "bounce",
                "msg":  fmt_bounce(symbol, tf, rsi_dir),
            })

    return messages


# ══════════════════════════════════════════════════════════════════════════════
#  POSTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

async def _post(bot, channel_id: str, msg: str, key: tuple):
    if _posted.get(key):
        return
    try:
        await bot.send_message(channel_id, msg, parse_mode="Markdown")
        _posted[key] = True
        await asyncio.sleep(0.5)
    except Exception as e:
        logger.error(f"Post error {key}: {e}")


def _trim_posted():
    if len(_posted) > 2000:
        for k in list(_posted)[:500]:
            del _posted[k]


# ══════════════════════════════════════════════════════════════════════════════
#  TIMEFRAME WATCHER
# ══════════════════════════════════════════════════════════════════════════════

async def _watch_tf(bot, channel_id: str, tf: str):
    while True:
        await asyncio.sleep(_seconds_until_close(tf) + 2)
        ck = _candle_key(tf)

        # Collect analysis for all symbols
        rsi_groups: dict[str, list[str]] = {}
        symbol_messages: dict[str, list] = {}

        for symbol in CHANNEL_SYMBOLS:
            try:
                result = await _analyze(symbol, tf)
                messages = _build_messages(result)
                symbol_messages[symbol] = messages

                # Collect RSI groups (Type 1 — posted once per TF across symbols)
                if result.get("extreme"):
                    lbl = result["rsi_lbl"]
                    rsi_groups.setdefault(lbl, []).append(symbol)

                await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"analyze error {symbol} {tf}: {e}")

        # Type 1: grouped RSI alert
        for lbl, syms in rsi_groups.items():
            await _post(bot, channel_id, fmt_rsi(tf, lbl, syms), ("rsi", tf, ck, lbl))

        # Types 2, 3, 4: per-symbol messages
        for symbol, msgs in symbol_messages.items():
            for item in msgs:
                await _post(bot, channel_id, item["msg"], (item["type"], symbol, tf, ck))

        # Type 5: CME close — Monday 00:10 UTC, triggered from 15m watcher
        if tf == "15m":
            now = datetime.now(timezone.utc)
            if now.weekday() == 0 and now.hour == 0 and 10 <= now.minute <= 12:
                cme_key = ("cme", now.date().isoformat())
                if not _posted.get(cme_key):
                    price = await fetch_cme_close()
                    if price:
                        await _post(bot, channel_id, fmt_cme(price), cme_key)

        _trim_posted()


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

async def channel_scheduler(bot, channel_id: str):
    """
    Runs forever. One watcher coroutine per timeframe, fires on candle close.
    Called by scheduler.py — runs as a managed task with auto-restart.
    """
    logger.info(f"Channel scheduler started — {len(SCAN_TIMEFRAMES)} timeframes, "
                f"{len(CHANNEL_SYMBOLS)} symbols")
    await asyncio.gather(*[
        _watch_tf(bot, channel_id, tf) for tf in SCAN_TIMEFRAMES
    ])
