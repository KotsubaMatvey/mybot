"""
ICT Scanner v2 — improved pattern detection
Patterns: FVG (unfilled), OB, BOS, CHoCH, Swings, Sweeps, Volume, Premium/Discount
Multi-timeframe confluence detection.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from config import SYMBOLS, TIMEFRAMES, CANDLE_LIMIT

BINANCE_BASE = "https://fapi.binance.com"
ALL_PATTERNS = ["FVG", "IFVG", "OB", "BOS", "CHoCH", "Swings", "Sweeps", "Volume", "PD"]


def ts_utc(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%H:%M")


async def fetch_candles(session, symbol, interval, limit=CANDLE_LIMIT):
    url = f"{BINANCE_BASE}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
        return [{"time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                  "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])} for c in data]
    except Exception:
        return []


# ── FVG (only unfilled) ───────────────────────────────────────────────────────
def detect_fvg(candles):
    """
    Find FVGs in last 20 candles. Only report if price hasn't returned to fill the gap.
    """
    results = []
    if len(candles) < 3:
        return results
    current_price = candles[-1]["close"]

    for i in range(2, min(20, len(candles))):
        c0 = candles[-(i+1)]
        c2 = candles[-(i-1)]

        # Bullish FVG: gap between c0.high and c2.low
        if c0["high"] < c2["low"]:
            gap_low, gap_high = c0["high"], c2["low"]
            # Check if price has filled (returned into) this gap
            subsequent = candles[-(i-1):]
            filled = any(c["low"] <= gap_high and c["high"] >= gap_low for c in subsequent)
            if not filled:
                results.append({
                    "type": "FVG", "direction": "Bullish",
                    "gap_low": gap_low, "gap_high": gap_high,
                    "time": c0["time"], "time2": c2["time"],
                    "detail": (f"FVG: {ts_utc(c0['time'])} | {ts_utc(c2['time'])} | "
                               f"{gap_low:.4f} - {gap_high:.4f} | Bullish FVG [UNFILLED]")
                })
                break  # report most recent

        # Bearish FVG
        elif c0["low"] > c2["high"]:
            gap_low, gap_high = c2["high"], c0["low"]
            subsequent = candles[-(i-1):]
            filled = any(c["low"] <= gap_high and c["high"] >= gap_low for c in subsequent)
            if not filled:
                results.append({
                    "type": "FVG", "direction": "Bearish",
                    "gap_low": gap_low, "gap_high": gap_high,
                    "time": c0["time"], "time2": c2["time"],
                    "detail": (f"FVG: {ts_utc(c0['time'])} | {ts_utc(c2['time'])} | "
                               f"{gap_low:.4f} - {gap_high:.4f} | Bearish FVG [UNFILLED]")
                })
                break
    return results




# ── IFVG (Inverse FVG — filled gap acting as S/R) ────────────────────────────
def detect_ifvg(candles):
    """
    IFVG: A FVG that was filled (price entered the gap zone) and now price
    returns to that zone again — the filled gap inverts into support/resistance.

    Steps:
    1. Find FVGs in candles[-50:-3]
    2. Confirm each was filled by subsequent candles
    3. Check if current price is re-entering that zone now
    """
    results = []
    if len(candles) < 10:
        return results

    current = candles[-1]
    scan_range = candles[:-2]  # leave last 2 candles as "current price check"

    for i in range(2, min(50, len(scan_range))):
        c0 = scan_range[-(i+1)]
        c2 = scan_range[-(i-1)]

        # Bullish FVG formed
        if c0["high"] < c2["low"]:
            gap_low, gap_high = c0["high"], c2["low"]
            # Check: was it filled? (any candle after c2 entered the gap)
            after = scan_range[-(i-1):]
            filled = any(c["low"] <= gap_high and c["high"] >= gap_low for c in after)
            if not filled:
                continue
            # Now check: is current price re-entering the gap zone?
            if gap_low <= current["close"] <= gap_high or gap_low <= current["low"] <= gap_high:
                results.append({
                    "type": "IFVG", "direction": "Bullish",
                    "gap_low": gap_low, "gap_high": gap_high,
                    "detail": (f"IFVG: {ts_utc(current['time'])} | "
                               f"{gap_low:.4f} - {gap_high:.4f} | "
                               f"Bullish IFVG (filled gap = support)")
                })
                break

        # Bearish FVG formed
        elif c0["low"] > c2["high"]:
            gap_low, gap_high = c2["high"], c0["low"]
            after = scan_range[-(i-1):]
            filled = any(c["low"] <= gap_high and c["high"] >= gap_low for c in after)
            if not filled:
                continue
            if gap_low <= current["close"] <= gap_high or gap_high >= current["high"] >= gap_low:
                results.append({
                    "type": "IFVG", "direction": "Bearish",
                    "gap_low": gap_low, "gap_high": gap_high,
                    "detail": (f"IFVG: {ts_utc(current['time'])} | "
                               f"{gap_low:.4f} - {gap_high:.4f} | "
                               f"Bearish IFVG (filled gap = resistance)")
                })
                break

    return results

# ── Order Block (proper ICT definition) ──────────────────────────────────────
def detect_ob(candles):
    """
    Bullish OB: last bearish candle before a BOS upward (price breaks swing high).
    Bearish OB: last bullish candle before a BOS downward.
    """
    results = []
    if len(candles) < 10:
        return results

    last = candles[-1]
    lookback = candles[-10:-1]
    swing_high = max(c["high"] for c in lookback)
    swing_low = min(c["low"] for c in lookback)

    # Bullish OB: price just broke above swing high
    if last["close"] > swing_high:
        for c in reversed(lookback):
            if c["close"] < c["open"]:  # bearish candle = bullish OB
                results.append({
                    "type": "OB", "direction": "Bullish",
                    "ob_high": c["high"], "ob_low": c["low"],
                    "detail": (f"OB: {ts_utc(c['time'])} | "
                               f"{c['low']:.4f} - {c['high']:.4f} | Bullish OB")
                })
                break

    # Bearish OB: price just broke below swing low
    elif last["close"] < swing_low:
        for c in reversed(lookback):
            if c["close"] > c["open"]:  # bullish candle = bearish OB
                results.append({
                    "type": "OB", "direction": "Bearish",
                    "ob_high": c["high"], "ob_low": c["low"],
                    "detail": (f"OB: {ts_utc(c['time'])} | "
                               f"{c['low']:.4f} - {c['high']:.4f} | Bearish OB")
                })
                break
    return results


# ── BOS (Break of Structure) ──────────────────────────────────────────────────
def detect_bos(candles):
    if len(candles) < 20:
        return []
    lookback = candles[-20:-1]
    last = candles[-1]
    swing_high = max(c["high"] for c in lookback)
    swing_low = min(c["low"] for c in lookback)
    if last["close"] > swing_high:
        return [{"type": "BOS", "direction": "Bullish", "level": swing_high,
                 "detail": f"BOS: {ts_utc(last['time'])} | {swing_high:.4f} | Bullish BOS"}]
    if last["close"] < swing_low:
        return [{"type": "BOS", "direction": "Bearish", "level": swing_low,
                 "detail": f"BOS: {ts_utc(last['time'])} | {swing_low:.4f} | Bearish BOS"}]
    return []


# ── CHoCH (Change of Character) ───────────────────────────────────────────────
def detect_choch(candles):
    """
    CHoCH: price breaks the LAST swing high/low in the OPPOSITE direction of trend.
    Trend up (higher highs) -> CHoCH when price breaks last swing low.
    Trend down (lower lows) -> CHoCH when price breaks last swing high.
    """
    if len(candles) < 30:
        return []

    # Find swing highs and lows in last 30 candles
    swing_highs = []
    swing_lows = []
    for i in range(1, len(candles) - 1):
        c = candles[i]
        if c["high"] > candles[i-1]["high"] and c["high"] > candles[i+1]["high"]:
            swing_highs.append(c["high"])
        if c["low"] < candles[i-1]["low"] and c["low"] < candles[i+1]["low"]:
            swing_lows.append(c["low"])

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return []

    last = candles[-1]
    # Uptrend: higher highs
    uptrend = swing_highs[-1] > swing_highs[-2]
    # Downtrend: lower lows
    downtrend = swing_lows[-1] < swing_lows[-2]

    # CHoCH bearish: uptrend but price breaks last swing low
    if uptrend and last["close"] < swing_lows[-1]:
        return [{"type": "CHoCH", "direction": "Bearish", "level": swing_lows[-1],
                 "detail": f"CHoCH: {ts_utc(last['time'])} | {swing_lows[-1]:.4f} | Bearish CHoCH ⚠️"}]
    # CHoCH bullish: downtrend but price breaks last swing high
    if downtrend and last["close"] > swing_highs[-1]:
        return [{"type": "CHoCH", "direction": "Bullish", "level": swing_highs[-1],
                 "detail": f"CHoCH: {ts_utc(last['time'])} | {swing_highs[-1]:.4f} | Bullish CHoCH ⚠️"}]
    return []


# ── Swings (Liquidity Pools) ──────────────────────────────────────────────────
def detect_swings(candles):
    if len(candles) < 3:
        return []
    c0, c1, c2 = candles[-3], candles[-2], candles[-1]
    if c1["high"] > c0["high"] and c1["high"] > c2["high"]:
        return [{"type": "Swings", "direction": "High", "level": c1["high"],
                 "detail": f"SWING: {ts_utc(c1['time'])} | {c1['high']:.4f} | Swing High"}]
    if c1["low"] < c0["low"] and c1["low"] < c2["low"]:
        return [{"type": "Swings", "direction": "Low", "level": c1["low"],
                 "detail": f"SWING: {ts_utc(c1['time'])} | {c1['low']:.4f} | Swing Low"}]
    return []


# ── Sweeps (Liquidity Sweeps) ─────────────────────────────────────────────────
def detect_sweeps(candles):
    if len(candles) < 20:
        return []
    lookback = candles[-20:-1]
    last = candles[-1]
    swing_high = max(c["high"] for c in lookback)
    swing_low = min(c["low"] for c in lookback)
    if last["high"] > swing_high and last["close"] < swing_high:
        return [{"type": "Sweeps", "direction": "Bearish", "level": swing_high,
                 "detail": f"SWEEP: {ts_utc(last['time'])} | {swing_high:.4f} | Bearish Sweep"}]
    if last["low"] < swing_low and last["close"] > swing_low:
        return [{"type": "Sweeps", "direction": "Bullish", "level": swing_low,
                 "detail": f"SWEEP: {ts_utc(last['time'])} | {swing_low:.4f} | Bullish Sweep"}]
    return []


# ── Volume ────────────────────────────────────────────────────────────────────
def detect_volume(candles):
    if len(candles) < 16:
        return []
    last = candles[-1]
    avg_vol = sum(c["volume"] for c in candles[-16:-1]) / 15
    if avg_vol == 0:
        return []
    if last["volume"] > avg_vol * 1.03:
        pct = ((last["volume"] / avg_vol) - 1) * 100
        usd_vol = last["volume"] * last["close"]
        usd_str = f"${usd_vol/1_000_000:.1f}M" if usd_vol >= 1_000_000 else f"${usd_vol/1_000:.0f}K"
        coin = last["volume"]
        detail = (f"VOLUME: {ts_utc(last['time'])} | "
                  f"{coin:.2f} coins ({usd_str}) | +{pct:.1f}% above avg")
        return [{"type": "Volume", "direction": "High", "level": coin, "detail": detail}]
    return []


# ── Premium / Discount Zones ──────────────────────────────────────────────────
def detect_pd_zones(candles):
    """
    Premium: price above 50% of last 50-candle range (sell zone).
    Discount: price below 50% of range (buy zone).
    Alert only when price enters the zone.
    """
    if len(candles) < 50:
        return []
    lookback = candles[-50:]
    hi = max(c["high"] for c in lookback)
    lo = min(c["low"] for c in lookback)
    eq = (hi + lo) / 2  # equilibrium
    last = candles[-1]
    prev = candles[-2]

    # Price just crossed above equilibrium into premium
    if prev["close"] <= eq < last["close"]:
        return [{"type": "PD", "direction": "Premium",
                 "detail": f"PREMIUM ZONE: {ts_utc(last['time'])} | EQ {eq:.4f} | Price entering premium (sell area)"}]
    # Price just crossed below equilibrium into discount
    if prev["close"] >= eq > last["close"]:
        return [{"type": "PD", "direction": "Discount",
                 "detail": f"DISCOUNT ZONE: {ts_utc(last['time'])} | EQ {eq:.4f} | Price entering discount (buy area)"}]
    return []


# ── Multi-timeframe confluence ────────────────────────────────────────────────
def check_confluence(symbol: str, results_by_tf: dict) -> list:
    """
    If same pattern type + direction appears on 2+ timeframes -> confluence alert.
    """
    tf_signals = {}
    for tf, patterns in results_by_tf.items():
        for p in patterns:
            key = (p["type"], p.get("direction", ""))
            tf_signals.setdefault(key, []).append(tf)

    confluences = []
    for (ptype, direction), tfs in tf_signals.items():
        if len(tfs) >= 2:
            tfs_str = " + ".join(sorted(tfs))
            confluences.append(
                f"🔥 {symbol} — CONFLUENCE: {ptype} {direction} on {tfs_str} — high probability setup"
            )
    return confluences


# ── Deduplication ─────────────────────────────────────────────────────────────
_sent: set = set()

def is_dup(symbol, tf, ptype, detail):
    key = f"{symbol}_{tf}_{ptype}_{detail[:50]}"
    if key in _sent:
        return True
    _sent.add(key)
    if len(_sent) > 30000:
        _sent.clear()
    return False


DETECTORS = {
    "FVG": detect_fvg,
    "IFVG": detect_ifvg,
    "OB": detect_ob,
    "BOS": detect_bos,
    "CHoCH": detect_choch,
    "Swings": detect_swings,
    "Sweeps": detect_sweeps,
    "Volume": detect_volume,
    "PD": detect_pd_zones,
}


# ── Zones snapshot (for /zones command) ───────────────────────────────────────
_active_zones: dict = {}  # {symbol: {tf: [patterns]}}

def get_active_zones():
    return dict(_active_zones)


async def run_scanner() -> tuple[list, list]:
    """Returns (alerts, confluence_messages)"""
    all_alerts = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_candles(session, sym, tf) for sym in SYMBOLS for tf in TIMEFRAMES]
        combos = [(sym, tf) for sym in SYMBOLS for tf in TIMEFRAMES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Store all candles for scoring
    all_candles = {}
    for (symbol, tf), candles in zip(combos, results):
        if not isinstance(candles, Exception) and candles:
            all_candles[(symbol, tf)] = candles

    # Reset zones
    global _active_zones
    _active_zones = {}

    by_symbol: dict = {sym: {} for sym in SYMBOLS}

    for (symbol, tf), candles in all_candles.items():
        tf_patterns = []
        detected_map = {}
        for pname, detector in DETECTORS.items():
            detected = detector(candles)
            for p in detected:
                tf_patterns.append(p)
                detected_map[pname] = p["detail"]
                if not is_dup(symbol, tf, pname, p["detail"]):
                    all_alerts.append({
                        "symbol": symbol,
                        "timeframe": tf,
                        "pattern": pname,
                        "detail": p["detail"],
                        "score": None,  # filled below
                        "_map": detected_map,
                    })

        if tf_patterns:
            by_symbol[symbol][tf] = tf_patterns
            _active_zones.setdefault(symbol, {})[tf] = tf_patterns

    # Calculate scores
    # Group alerts by (symbol, tf) to score together
    from collections import defaultdict
    grouped = defaultdict(dict)
    grouped_alerts = defaultdict(list)
    for a in all_alerts:
        key = (a["symbol"], a["timeframe"])
        grouped[key][a["pattern"]] = a["detail"]
        grouped_alerts[key].append(a)

    for key, patterns in grouped.items():
        symbol, tf = key
        s = score_signal(symbol, tf, patterns, all_candles)
        for a in grouped_alerts[key]:
            a["score"] = s
        # clean internal key
    for a in all_alerts:
        a.pop("_map", None)

    # Check confluence per symbol
    all_confluences = []
    for symbol, tf_data in by_symbol.items():
        if len(tf_data) >= 2:
            msgs = check_confluence(symbol, tf_data)
            for msg in msgs:
                all_confluences.append({"symbol": symbol, "message": msg})

    return all_alerts, all_confluences, all_candles


# ── Signal Scoring ────────────────────────────────────────────────────────────
def score_signal(symbol: str, timeframe: str, patterns: dict, all_candles: dict) -> int:
    """
    Scores a signal from 1 to 5 based on context quality.
    Criteria:
    +1 — Multiple patterns on same candle (e.g. FVG + OB together)
    +1 — Confluence with higher timeframe trend
    +1 — Abnormal volume present
    +1 — CHoCH or BOS present (structural confirmation)
    +1 — IFVG present (extra confluence)
    Max score: 5
    """
    score = 0

    # +1 if 2+ patterns detected on this symbol/tf
    if len(patterns) >= 2:
        score += 1

    # +1 if volume spike present
    if "Volume" in patterns:
        score += 1

    # +1 if structural pattern present (BOS or CHoCH)
    if "BOS" in patterns or "CHoCH" in patterns:
        score += 1

    # +1 if IFVG present (filled gap acting as S/R = high quality)
    if "IFVG" in patterns:
        score += 1

    # +1 if same pattern appears on a higher timeframe (multi-tf confirmation)
    tf_hierarchy = ["5m", "15m", "30m", "1h", "4h", "1d"]
    try:
        tf_idx = tf_hierarchy.index(timeframe)
    except ValueError:
        tf_idx = 0

    higher_tfs = tf_hierarchy[tf_idx + 1:]
    pattern_types = set(patterns.keys())
    for htf in higher_tfs:
        htf_key = (symbol, htf)
        htf_candles = all_candles.get(htf_key, [])
        if not htf_candles:
            continue
        for pname, detector in DETECTORS.items():
            if pname in pattern_types:
                try:
                    result = detector(htf_candles)
                    if result:
                        score += 1
                        break
                except Exception:
                    pass
        break  # only check next timeframe up

    return min(score, 5)


def score_to_stars(score: int) -> str:
    filled = "★" * score
    empty = "☆" * (5 - score)
    labels = {1: "Weak", 2: "Moderate", 3: "Good", 4: "Strong", 5: "Very Strong"}
    return f"{filled}{empty} {score}/5 — {labels.get(score, '')}"
