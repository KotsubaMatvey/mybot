"""
Classic TA scanner — replicates Better Trader Insights channel logic exactly.

Message types:
  1. RSI alert     — short, groups symbols, no price/OB
  2. Pattern alert — Pinbar/Predict/Engulfing with OB, no entry/SL
  3. Setup         — Scalp/Trend Long/Short with entry, SL, TP, time limit, OB
  4. Bounce        — "Возможен отскок/откат" when RSI extreme + OB confirm
  5. CME close     — posted at 00:10 UTC on weekdays
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

BINANCE_FUTURES_API = "https://fapi.binance.com"
BINANCE_SPOT_API    = "https://api.binance.com"
COINBASE_API        = "https://api.exchange.coinbase.com"

# Fixed symbols — independent from bot settings
CHANNEL_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
SCAN_TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]

TF_SECONDS = {
    "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400, "1d": 86400,
}

# Dedup: (symbol, tf, candle_open_time, msg_type) → True
_posted: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  TIMING
# ══════════════════════════════════════════════════════════════════════════════

def seconds_until_next_close(tf: str) -> float:
    period = TF_SECONDS.get(tf, 60)
    now    = datetime.now(timezone.utc).timestamp()
    last   = (int(now) // period) * period
    return max(last + period - now, 0)

def candle_key(tf: str) -> int:
    period = TF_SECONDS.get(tf, 60)
    now    = int(datetime.now(timezone.utc).timestamp())
    return (now // period) * period


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHING
# ══════════════════════════════════════════════════════════════════════════════

async def fetch_candles(symbol: str, interval: str, limit: int = 100) -> list:
    url    = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        return [{"time": int(d[0]), "open": float(d[1]), "high": float(d[2]),
                 "low": float(d[3]), "close": float(d[4]), "volume": float(d[5])}
                for d in data]
    except Exception as e:
        logger.error(f"fetch_candles {symbol} {interval}: {e}")
        return []


async def fetch_spot_orderbook(symbol: str) -> dict:
    """Binance SPOT orderbook — used for OB analysis as Better Trader does."""
    url    = f"{BINANCE_SPOT_API}/api/v3/depth"
    params = {"symbol": symbol, "limit": 500}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        return {
            "bids": [(float(p), float(q)) for p, q in data.get("bids", [])],
            "asks": [(float(p), float(q)) for p, q in data.get("asks", [])],
            "source": "BINANCE",
        }
    except Exception as e:
        logger.error(f"spot OB {symbol}: {e}")
        return {"bids": [], "asks": [], "source": "BINANCE"}


async def fetch_coinbase_orderbook(symbol: str) -> dict:
    """Coinbase orderbook for BTC — Better Trader uses BTCUSD (COINBASE)."""
    cb_symbol = "BTC-USD" if "BTC" in symbol else "ETH-USD"
    url = f"{COINBASE_API}/products/{cb_symbol}/book?level=2"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        return {
            "bids": [(float(p[0]), float(p[1])) for p in data.get("bids", [])[:200]],
            "asks": [(float(p[0]), float(p[1])) for p in data.get("asks", [])[:200]],
            "source": "COINBASE",
        }
    except Exception as e:
        logger.error(f"coinbase OB {symbol}: {e}")
        return {"bids": [], "asks": [], "source": "COINBASE"}


async def fetch_cme_close() -> float | None:
    """Try to get CME BTC futures close price via Binance BTC1! proxy (weekly)."""
    try:
        # Use BTCUSDT weekly close as proxy for CME
        url    = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
        params = {"symbol": "BTCUSDT", "interval": "1w", "limit": 2}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        if data and len(data) >= 1:
            return float(data[-2][4])  # previous week close
    except Exception as e:
        logger.error(f"CME close: {e}")
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  INDICATORS
# ══════════════════════════════════════════════════════════════════════════════

def calc_rsi(candles: list, period: int = 14) -> float | None:
    if len(candles) < period + 1:
        return None
    closes = [c["close"] for c in candles[-(period + 1):]]
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 1)


def rsi_state(rsi: float) -> tuple[str, str]:
    """Returns (label_ru, direction)"""
    if rsi >= 80:   return "Strongly overbought",  "bearish"
    if rsi >= 70:   return "Slightly overbought",  "bearish"
    if rsi <= 20:   return "Strongly oversold",   "bullish"
    if rsi <= 30:   return "Slightly oversold",  "bullish"
    return "Neutral", "neutral"


def analyze_ob(ob: dict, price: float) -> dict:
    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    if not bids or not asks:
        return {}
    zone = price * 0.01
    sup_bids = [(p, q) for p, q in bids if price - zone <= p <= price]
    res_asks = [(p, q) for p, q in asks if price <= p <= price + zone]
    sup_qty  = round(sum(q for _, q in sup_bids), 1)
    res_qty  = round(sum(q for _, q in res_asks), 1)
    wide     = price * 0.02
    total_b  = sum(q for p, q in bids if p >= price - wide)
    total_a  = sum(q for p, q in asks if p <= price + wide)
    dominant = "bids" if total_b >= total_a else "asks"
    return {
        "dominant":   dominant,
        "source":     ob.get("source", "BINANCE"),
        "support":    (round(price - zone, 1), round(price, 1), sup_qty),
        "resistance": (round(price, 1), round(price + zone, 1), res_qty),
        "ticker":     "BTC.P" if "BTC" in str(ob.get("source","")) or True else "ETH.P",
    }


def detect_pattern(candles: list) -> tuple[str, str] | None:
    if len(candles) < 3:
        return None
    c = candles[-2]
    p = candles[-3]
    body  = abs(c["close"] - c["open"])
    rng   = c["high"] - c["low"]
    if rng == 0:
        return None
    ratio = body / rng
    uw    = c["high"] - max(c["close"], c["open"])
    lw    = min(c["close"], c["open"]) - c["low"]
    # Pinbar
    if ratio < 0.35:
        if lw > body * 2 and lw > uw * 2:  return "Pinbar", "bullish"
        if uw > body * 2 and uw > lw * 2:  return "Pinbar", "bearish"
    # Engulfing → "Предикт" (Better Trader uses this term)
    pb = abs(p["close"] - p["open"])
    if body > pb * 1.5:
        if c["close"] > c["open"] and p["close"] < p["open"]: return "Predict", "bullish"
        if c["close"] < c["open"] and p["close"] > p["open"]: return "Predict", "bearish"
    # Doji
    if ratio < 0.1:
        return "Predict", "neutral"
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  MESSAGE FORMATTERS
# ══════════════════════════════════════════════════════════════════════════════

def season_emoji() -> str:
    m = datetime.now(timezone.utc).month
    if m in (3, 4, 5):   return "🍀"
    if m in (6, 7, 8):   return "🍀"
    if m in (9, 10, 11): return "🍂"
    return "❄️"

def fmt_price(p: float) -> str:
    return f"{p:,.1f}" if p > 100 else f"{p:.4f}"

def fmt_ts() -> str:
    return datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S")

def ob_ticker(symbol: str) -> str:
    return "BTC.P" if "BTC" in symbol else "ETH.P"


def msg_rsi(tf: str, label: str, symbols_affected: list) -> str:
    """
    Type 1 — RSI only, short.
    ⚠️ 1H Сильно перепродано
    #BTCUSDT, #ETHUSDT
    17-Oct-2025 10:01:01
    """
    emoji  = "⚠️" if "Strongly" in label else "☀️"
    tags   = ", ".join(f"#{s}" for s in symbols_affected)
    return f"{emoji} *{tf} {label}*\n{tags}\n_{fmt_ts()}_"


def msg_pattern(symbol: str, tf: str, pattern: str, direction: str,
                price: float, ob: dict, exchange: str = "BINANCE") -> str:
    """
    Type 2 — Pattern with OB, no entry/SL.
    🍀 30M 👁 Предикт, возможен разворот вверх #BTCUSDT.P (BINANCE), текущая цена 105132.1

    Стакан: 📗 бидов больше
    179 BTC.P поддержка: 104080.8 - 105132.1
    137 BTC.P сопротивление: 105132.1 - 106183.4
    17-Oct-2025 11:30:02
    """
    se     = season_emoji()
    p_emoji = "👁" if pattern == "Predict" else "🔪"
    dir_ru = "up" if direction == "bullish" else "down"
    ob_dom = "📗 more bids" if ob.get("dominant") == "bids" else "📕 more asks"
    sup    = ob.get("support",    (0.0, 0.0, 0.0))
    res    = ob.get("resistance", (0.0, 0.0, 0.0))
    sup    = tuple(v or 0.0 for v in sup)
    res    = tuple(v or 0.0 for v in res)
    tk     = ob_ticker(symbol)
    tag    = f"#{symbol}.P" if exchange == "BINANCE" else f"#{symbol[:3]}USD"

    lines = [
        f"{se} *{tf} {p_emoji} {pattern}, possible reversal {dir_ru} {tag} ({exchange})*, price {fmt_price(price)}",
        "",
        f"Order book: {ob_dom}",
        f"{fmt_price(sup[2])} {tk} support: {fmt_price(sup[0])} - {fmt_price(sup[1])}",
        f"{fmt_price(res[2])} {tk} resistance: {fmt_price(res[0])} - {fmt_price(res[1])}",
        f"_{fmt_ts()}_",
    ]
    return "\n".join(lines)


def msg_setup(symbol: str, tf: str, trade_type: str, price: float,
              sl: float, tp1: float, tp2: float, tp3: float,
              ob: dict, exchange: str = "BINANCE") -> str:
    """
    Type 3 — Full setup with entry/SL/TP + time limit + OB.
    🍀 4H ⚡ Скальп Лонг #BTCUSDT.P (BINANCE), текущая цена 113355.2

    Вход: 113355.2
    Стоп-лосс: 110180

    Цели:
    ▪️ 30% на 115055.5
    ▪️ 30% на 116755.9
    ▪️ 40% на 118456.2
    ▪️ Закройте позицию через 20 часов (в 22.10.2025 15:00)

    Стакан: 📕 асков больше
    122 BTC.P поддержка: 112221.6 - 113355.2
    179 BTC.P сопротивление: 113355.2 - 114488.8
    21-Oct-2025 19:00:10
    """
    se      = season_emoji()
    is_long = "Long" in trade_type
    t_emoji = "⚡" if "Scalp" in trade_type else "↗️" if is_long else "↘️"
    ob_dom  = "📗 more bids" if ob.get("dominant") == "bids" else "📕 more asks"
    sup     = ob.get("support",    (0.0, 0.0, 0.0))
    res     = ob.get("resistance", (0.0, 0.0, 0.0))
    sup     = tuple(v or 0.0 for v in sup)
    res     = tuple(v or 0.0 for v in res)
    tk      = ob_ticker(symbol)
    tag     = f"#{symbol}.P" if exchange == "BINANCE" else f"#{symbol[:3]}USD"

    # Time limit: +20h from now
    close_time = datetime.now(timezone.utc) + timedelta(hours=20)
    close_str  = close_time.strftime("%d.%m.%Y %H:%M")

    lines = [
        f"{se} *{tf} {t_emoji} {trade_type} {tag} ({exchange})*, price {fmt_price(price)}",
        "",
        f"Entry: {fmt_price(price)}",
        f"Stop-loss: {fmt_price(sl)}",
        "",
        "Targets:",
        f"▪️ 30% at {fmt_price(tp1)}",
        f"▪️ 30% at {fmt_price(tp2)}",
        f"▪️ 40% at {fmt_price(tp3)}",
        f"▪️ Close position in 20 hours (at {close_str})",
        "",
        f"Order book: {ob_dom}",
        f"{fmt_price(sup[2])} {tk} support: {fmt_price(sup[0])} - {fmt_price(sup[1])}",
        f"{fmt_price(res[2])} {tk} resistance: {fmt_price(res[0])} - {fmt_price(res[1])}",
        f"_{fmt_ts()}_",
    ]
    return "\n".join(lines)


def msg_bounce(symbol: str, tf: str, direction: str) -> str:
    """
    Type 4 — Bounce/pullback signal.
    🍀 1H ☀️ Возможен отскок вверх #BTCUSDT.P, #TOTAL3
    """
    se     = season_emoji()
    action = "bounce up" if direction == "bullish" else "pullback down"
    tag    = f"#{symbol}.P"
    return f"{se} *{tf} ☀️ Possible {action} {tag}*\n_{fmt_ts()}_"


def msg_cme(price: float) -> str:
    """CME (BTC1!) закрылся на 107220"""
    return f"☀️ *CME (BTC1!) closed at {fmt_price(price)}*\n_{fmt_ts()}_"


# ══════════════════════════════════════════════════════════════════════════════
#  SIGNAL LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def compute_sl_tp(candles: list, direction: str, price: float):
    lookback = candles[-20:]
    hi  = max(c["high"] for c in lookback)
    lo  = min(c["low"]  for c in lookback)
    rng = hi - lo
    if direction == "bullish":
        sl  = round(lo - rng * 0.015, 2)
        tp1 = round(price + rng * 0.25, 2)
        tp2 = round(price + rng * 0.50, 2)
        tp3 = round(price + rng * 0.85, 2)
    else:
        sl  = round(hi + rng * 0.015, 2)
        tp1 = round(price - rng * 0.25, 2)
        tp2 = round(price - rng * 0.50, 2)
        tp3 = round(price - rng * 0.85, 2)
    return sl, tp1, tp2, tp3


async def analyze_symbol_tf(symbol: str, tf: str) -> list[dict]:
    """
    Returns list of messages to post for this symbol+tf combo.
    Each item: {"type": str, "msg": str, "rsi_label": str, "direction": str}
    """
    results = []

    candles = await fetch_candles(symbol, tf, limit=100)
    if not candles:
        return results

    price = candles[-1]["close"]
    rsi   = calc_rsi(candles)
    if rsi is None:
        return results

    rsi_lbl, rsi_dir = rsi_state(rsi)
    pattern = detect_pattern(candles)

    # Fetch OB from Binance spot
    ob_raw  = await fetch_spot_orderbook(symbol)
    ob_data = analyze_ob(ob_raw, price)
    ob_dom  = ob_data.get("dominant", "neutral")

    # ── TYPE 1: RSI alert
    # Post if RSI >= 70 or <= 30. Grouped per-tf across symbols in scheduler.
    rsi_triggered = rsi <= 30 or rsi >= 70

    # ── TYPE 2: Pattern (Pinbar / Предикт) — post if pattern found, direction confirmed
    if pattern and pattern[1] != "neutral":
        pat_name, pat_dir = pattern
        # Direction confirmed by OB or RSI
        ob_confirms  = (ob_dom == "bids" and pat_dir == "bullish") or \
                       (ob_dom == "asks" and pat_dir == "bearish")
        rsi_confirms = (rsi_dir == "bullish" and pat_dir == "bullish") or \
                       (rsi_dir == "bearish" and pat_dir == "bearish")
        if ob_confirms or rsi_confirms:
            msg = msg_pattern(symbol, tf, pat_name, pat_dir, price, ob_data)
            results.append({"type": "pattern", "msg": msg, "direction": pat_dir})

            # ── TYPE 3: Setup — only on 1h/4h/1d + strong confluence (all 3 signals agree)
            if tf in ("1h", "4h", "1d"):
                bull = int(rsi_dir == "bullish") + int(ob_dom == "bids") + int(pat_dir == "bullish")
                bear = int(rsi_dir == "bearish") + int(ob_dom == "asks") + int(pat_dir == "bearish")
                if bull == 3 or bear == 3:
                    direction  = "bullish" if bull == 3 else "bearish"
                    is_long    = direction == "bullish"
                    # Scalp on 1h, Trend on 4h/1d
                    trade_type = ("Scalp" if tf == "1h" else "Trend") + \
                                 (" Long" if is_long else " Short")
                    sl, tp1, tp2, tp3 = compute_sl_tp(candles, direction, price)
                    msg2 = msg_setup(symbol, tf, trade_type, price, sl, tp1, tp2, tp3, ob_data)
                    results.append({"type": "setup", "msg": msg2, "direction": direction})

    # ── TYPE 4: Bounce — RSI extreme + OB confirm, no pattern needed
    if rsi_triggered and not pattern:
        if (rsi_dir == "bullish" and ob_dom == "bids") or \
           (rsi_dir == "bearish" and ob_dom == "asks"):
            direction = rsi_dir
            msg = msg_bounce(symbol, tf, direction)
            results.append({"type": "bounce", "msg": msg, "direction": direction})

    return results, rsi_lbl if rsi_triggered else None, rsi_dir if rsi_triggered else None


# ══════════════════════════════════════════════════════════════════════════════
#  SCHEDULER
# ══════════════════════════════════════════════════════════════════════════════

async def channel_scheduler(bot, channel_id: str):
    """
    Runs forever. One watcher per timeframe, fires exactly on candle close.
    RSI alerts are grouped: if BTC and ETH both oversold on same TF → one message.
    """
    logger.info("Channel scheduler started")

    async def watch_tf(tf: str):
        while True:
            wait = seconds_until_next_close(tf)
            await asyncio.sleep(wait + 2)  # +2s buffer

            ck = candle_key(tf)

            # ── Collect RSI states for all symbols on this TF
            rsi_groups: dict[str, list[str]] = {}  # label → [symbols]
            all_results = {}

            for symbol in CHANNEL_SYMBOLS:
                try:
                    res = await analyze_symbol_tf(symbol, tf)
                    msgs, rsi_lbl, rsi_dir = res
                    all_results[symbol] = msgs

                    # Group RSI
                    if rsi_lbl:
                        rsi_groups.setdefault(rsi_lbl, []).append(symbol)

                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.error(f"analyze {symbol} {tf}: {e}")

            # ── Post grouped RSI alert (Type 1)
            for rsi_lbl, syms in rsi_groups.items():
                key = ("rsi", tf, ck, rsi_lbl)
                if _posted.get(key):
                    continue
                try:
                    msg = msg_rsi(tf, rsi_lbl, syms)
                    await bot.send_message(channel_id, msg, parse_mode="Markdown")
                    _posted[key] = True
                    logger.info(f"RSI post: {tf} {rsi_lbl} {syms}")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"RSI post error: {e}")

            # ── Post per-symbol pattern/setup/bounce (Types 2, 3, 4)
            for symbol, msgs in all_results.items():
                for item in msgs:
                    key = (item["type"], symbol, tf, ck)
                    if _posted.get(key):
                        continue
                    try:
                        await bot.send_message(channel_id, item["msg"], parse_mode="Markdown")
                        _posted[key] = True
                        logger.info(f"{item['type']} post: {symbol} {tf}")
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Post error {symbol} {tf}: {e}")

            # ── CME close: post at 00:10 UTC on Mon (weekly close)
            now_utc = datetime.now(timezone.utc)
            if tf == "15m" and now_utc.hour == 0 and 10 <= now_utc.minute <= 12 \
                    and now_utc.weekday() == 0:  # Monday
                key = ("cme", now_utc.date().isoformat())
                if not _posted.get(key):
                    cme_price = await fetch_cme_close()
                    if cme_price:
                        try:
                            await bot.send_message(channel_id, msg_cme(cme_price),
                                                   parse_mode="Markdown")
                            _posted[key] = True
                        except Exception as e:
                            logger.error(f"CME post error: {e}")

            # Clean memory
            if len(_posted) > 2000:
                oldest = sorted(_posted.keys(),
                                key=lambda x: x[-1] if isinstance(x[-1], int) else 0)[:500]
                for k in oldest:
                    del _posted[k]

    await asyncio.gather(*[watch_tf(tf) for tf in SCAN_TIMEFRAMES])


# Legacy stub
async def run_classic_scanner(symbols: list = None) -> list:
    return []
