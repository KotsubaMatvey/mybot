"""
classic_indicators.py — RSI, pattern detection, orderbook analysis.
Pure functions — no I/O, no side effects.
"""
from datetime import datetime, timezone


# ══════════════════════════════════════════════════════════════════════════════
#  RSI
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
    """Returns (label, direction). direction: bullish | bearish | neutral."""
    if rsi >= 80: return "Strongly overbought", "bearish"
    if rsi >= 70: return "Slightly overbought", "bearish"
    if rsi <= 20: return "Strongly oversold",   "bullish"
    if rsi <= 30: return "Slightly oversold",   "bullish"
    return "Neutral", "neutral"


def rsi_is_extreme(rsi: float) -> bool:
    return rsi <= 30 or rsi >= 70


# ══════════════════════════════════════════════════════════════════════════════
#  CANDLE PATTERN DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def detect_pattern(candles: list) -> tuple[str, str] | None:
    """
    Returns (pattern_name, direction) or None.
    Checks the second-to-last closed candle (candles[-2]).
    Patterns: Pinbar, Predict (engulfing), Doji.
    """
    if len(candles) < 3:
        return None

    c = candles[-2]  # last closed candle
    p = candles[-3]  # previous candle

    body = abs(c["close"] - c["open"])
    rng  = c["high"] - c["low"]
    if rng == 0:
        return None

    ratio = body / rng
    uw    = c["high"] - max(c["close"], c["open"])  # upper wick
    lw    = min(c["close"], c["open"]) - c["low"]   # lower wick

    # Pinbar — small body, dominant wick
    if ratio < 0.35:
        if lw > body * 2 and lw > uw * 2:
            return "Pinbar", "bullish"
        if uw > body * 2 and uw > lw * 2:
            return "Pinbar", "bearish"

    # Predict (engulfing) — current body > 1.5x previous body
    prev_body = abs(p["close"] - p["open"])
    if body > prev_body * 1.5:
        if c["close"] > c["open"] and p["close"] < p["open"]:
            return "Predict", "bullish"
        if c["close"] < c["open"] and p["close"] > p["open"]:
            return "Predict", "bearish"

    # Doji — nearly no body
    if ratio < 0.1:
        return "Predict", "neutral"

    return None


# ══════════════════════════════════════════════════════════════════════════════
#  ORDERBOOK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def analyze_ob(ob: dict, price: float) -> dict:
    """
    Analyze orderbook around current price.
    Returns support/resistance zones and dominant side.
    """
    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    if not bids or not asks:
        return {"dominant": "neutral", "source": ob.get("source", "BINANCE"),
                "support": (0.0, 0.0, 0.0), "resistance": (0.0, 0.0, 0.0)}

    zone = price * 0.01   # 1% zone around price
    wide = price * 0.02   # 2% zone for dominance check

    sup_qty = round(sum(q for p, q in bids if price - zone <= p <= price), 1)
    res_qty = round(sum(q for p, q in asks if price <= p <= price + zone), 1)

    total_b = sum(q for p, q in bids if p >= price - wide)
    total_a = sum(q for p, q in asks if p <= price + wide)
    dominant = "bids" if total_b >= total_a else "asks"

    return {
        "dominant":   dominant,
        "source":     ob.get("source", "BINANCE"),
        "support":    (round(price - zone, 1), round(price, 1), sup_qty),
        "resistance": (round(price, 1), round(price + zone, 1), res_qty),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  SL / TP CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def compute_sl_tp(candles: list, direction: str, price: float) -> tuple:
    lookback = candles[-20:]
    hi  = max(c["high"] for c in lookback)
    lo  = min(c["low"]  for c in lookback)
    rng = hi - lo
    if direction == "bullish":
        return (
            round(lo - rng * 0.015, 2),
            round(price + rng * 0.25, 2),
            round(price + rng * 0.50, 2),
            round(price + rng * 0.85, 2),
        )
    else:
        return (
            round(hi + rng * 0.015, 2),
            round(price - rng * 0.25, 2),
            round(price - rng * 0.50, 2),
            round(price - rng * 0.85, 2),
        )
