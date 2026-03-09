"""
ICT Scanner v2 — improved pattern detection
Patterns: FVG (unfilled), OB, BOS, CHoCH, Swings, Sweeps, Volume, Premium/Discount
Multi-timeframe confluence detection.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from config import SYMBOLS, TIMEFRAMES, CANDLE_LIMIT

# Module-level candle cache — updated every scan, read by chart requests
_candle_cache: dict = {}  # {(symbol, tf): [candle, ...]}
_pattern_cache: dict = {}  # {(symbol, tf): [alert_dict, ...]}


def get_cached_candles(symbol: str, tf: str) -> list:
    """Return last known candles for symbol+tf. Empty list if not yet scanned."""
    return _candle_cache.get((symbol, tf), [])


def get_cached_patterns(symbol: str, tf: str) -> list:
    """Return last known detected patterns for symbol+tf. Empty list if none."""
    return _pattern_cache.get((symbol, tf), [])

BINANCE_BASE = "https://fapi.binance.com"
ALL_PATTERNS = ["FVG", "IFVG", "OB", "BOS", "CHoCH", "Swings", "Sweeps", "Volume", "PD"]


def ts_utc(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%H:%M")

def fmt_price(p: float) -> str:
    """Consistent price formatting: 66445.1 / 1.85 / 0.0023"""
    if p >= 1000: return f"{p:,.1f}"
    if p >= 1:    return f"{p:.2f}"
    return f"{p:.4f}"


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
                               f"{fmt_price(gap_low)} - {fmt_price(gap_high)} | Bullish FVG [UNFILLED]")
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
                               f"{fmt_price(gap_low)} - {fmt_price(gap_high)} | Bearish FVG [UNFILLED]")
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
                               f"{fmt_price(gap_low)} - {fmt_price(gap_high)} | "
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
                               f"{fmt_price(gap_low)} - {fmt_price(gap_high)} | "
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
                               f"{fmt_price(c['low'])} - {fmt_price(c['high'])} | Bullish OB")
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
                               f"{fmt_price(c['low'])} - {fmt_price(c['high'])} | Bearish OB")
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
                 "detail": f"BOS: {ts_utc(last['time'])} | {fmt_price(swing_high)} | Bullish BOS"}]
    if last["close"] < swing_low:
        return [{"type": "BOS", "direction": "Bearish", "level": swing_low,
                 "detail": f"BOS: {ts_utc(last['time'])} | {fmt_price(swing_low)} | Bearish BOS"}]
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
                 "detail": f"CHoCH: {ts_utc(last['time'])} | {fmt_price(swing_lows[-1])} | Bearish CHoCH ⚠️"}]
    # CHoCH bullish: downtrend but price breaks last swing high
    if downtrend and last["close"] > swing_highs[-1]:
        return [{"type": "CHoCH", "direction": "Bullish", "level": swing_highs[-1],
                 "detail": f"CHoCH: {ts_utc(last['time'])} | {fmt_price(swing_highs[-1])} | Bullish CHoCH ⚠️"}]
    return []


# ── Swings (Liquidity Pools) ──────────────────────────────────────────────────
def detect_swings(candles):
    if len(candles) < 3:
        return []
    c0, c1, c2 = candles[-3], candles[-2], candles[-1]
    if c1["high"] > c0["high"] and c1["high"] > c2["high"]:
        return [{"type": "Swings", "direction": "High", "level": c1["high"],
                 "detail": f"SWING: {ts_utc(c1['time'])} | {fmt_price(c1['high'])} | Swing High"}]
    if c1["low"] < c0["low"] and c1["low"] < c2["low"]:
        return [{"type": "Swings", "direction": "Low", "level": c1["low"],
                 "detail": f"SWING: {ts_utc(c1['time'])} | {fmt_price(c1['low'])} | Swing Low"}]
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
                 "detail": f"SWEEP: {ts_utc(last['time'])} | {fmt_price(swing_high)} | Bearish Sweep"}]
    if last["low"] < swing_low and last["close"] > swing_low:
        return [{"type": "Sweeps", "direction": "Bullish", "level": swing_low,
                 "detail": f"SWEEP: {ts_utc(last['time'])} | {fmt_price(swing_low)} | Bullish Sweep"}]
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
                 "detail": f"PREMIUM ZONE: {ts_utc(last['time'])} | EQ {fmt_price(eq)} | Price entering premium (sell area)"}]
    # Price just crossed below equilibrium into discount
    if prev["close"] >= eq > last["close"]:
        return [{"type": "PD", "direction": "Discount",
                 "detail": f"DISCOUNT ZONE: {ts_utc(last['time'])} | EQ {fmt_price(eq)} | Price entering discount (buy area)"}]
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
# Key: (symbol, tf, pattern_type, direction, price_level_rounded, candle_timestamp)
# This prevents re-alerting the same structural signal until price moves significantly
_sent: dict = {}

def _price_bucket(price: float) -> int:
    """Round price to 0.5% bucket to group nearby levels."""
    if price <= 0:
        return 0
    bucket_size = price * 0.005
    return int(price / bucket_size)

def is_dup(symbol: str, tf: str, ptype: str, pattern: dict) -> bool:
    direction = pattern.get("direction", "")
    # Use candle timestamp if available, else price bucket
    ts    = pattern.get("time", 0)
    level = pattern.get("gap_low") or pattern.get("level") or pattern.get("ob_low", 0)
    pbkt  = _price_bucket(level)
    key   = (symbol, tf, ptype, direction, pbkt, ts)
    if key in _sent:
        return True
    _sent[key] = True
    # Cleanup: keep only last 5000 keys
    if len(_sent) > 5000:
        oldest = list(_sent.keys())[:500]
        for k in oldest:
            del _sent[k]
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


# Semaphore: max 5 concurrent Binance API requests
_sem = asyncio.Semaphore(5)

async def _fetch_with_sem(session, symbol, tf):
    async with _sem:
        return await fetch_candles(session, symbol, tf)


async def run_scanner() -> tuple[list, list, dict]:
    """Returns (alerts, confluence_messages, all_candles)"""
    from collections import defaultdict
    all_alerts = []

    # ── 1. Fetch all candles in parallel with connection reuse
    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        combos  = [(sym, tf) for sym in SYMBOLS for tf in TIMEFRAMES]
        tasks   = [_fetch_with_sem(session, sym, tf) for sym, tf in combos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_candles: dict = {}
    for (symbol, tf), candles in zip(combos, results):
        if not isinstance(candles, Exception) and candles:
            all_candles[(symbol, tf)] = candles
            _candle_cache[(symbol, tf)] = candles

    # ── 2. Run all detectors ONCE per (symbol, tf) — cache results
    # detection_cache: {(symbol, tf): {pname: [pattern_dict, ...]}}
    detection_cache: dict = {}
    for (symbol, tf), candles in all_candles.items():
        detection_cache[(symbol, tf)] = {}
        for pname, detector in DETECTORS.items():
            try:
                detected = detector(candles)
                if detected:
                    detection_cache[(symbol, tf)][pname] = detected
            except Exception:
                pass

    # ── 3. Build alerts from cache (dedup check here)
    global _active_zones
    _active_zones = {}
    by_symbol: dict = {sym: {} for sym in SYMBOLS}

    for (symbol, tf), pname_map in detection_cache.items():
        tf_patterns = []
        for pname, detected in pname_map.items():
            for p in detected:
                tf_patterns.append(p)
                if not is_dup(symbol, tf, pname, p):
                    all_alerts.append({
                        "symbol":    symbol,
                        "timeframe": tf,
                        "pattern":   pname,
                        "detail":    p["detail"],
                        "direction": p.get("direction", ""),
                        "score":     None,  # filled below
                    })
        if tf_patterns:
            by_symbol[symbol][tf] = tf_patterns
            _active_zones.setdefault(symbol, {})[tf] = tf_patterns

    # ── 4. Score signals — reuse detection_cache, no extra API calls
    grouped         = defaultdict(dict)
    grouped_alerts  = defaultdict(list)
    for a in all_alerts:
        key = (a["symbol"], a["timeframe"])
        grouped[key][a["pattern"]] = a["detail"]
        grouped_alerts[key].append(a)

    for key, patterns in grouped.items():
        symbol, tf = key
        s = score_signal(symbol, tf, patterns, detection_cache)
        for a in grouped_alerts[key]:
            a["score"] = s

    # ── 5. Confluence per symbol
    all_confluences = []
    for symbol, tf_data in by_symbol.items():
        if len(tf_data) >= 2:
            for msg in check_confluence(symbol, tf_data):
                all_confluences.append({"symbol": symbol, "message": msg})

    # Update pattern cache
    _pattern_cache.clear()
    for a in all_alerts:
        key = (a["symbol"], a["timeframe"])
        _pattern_cache.setdefault(key, []).append(a)

    return all_alerts, all_confluences, all_candles


# ══════════════════════════════════════════════════════════════════════════════
#  SIGNAL SCORING — weighted confidence model
# ══════════════════════════════════════════════════════════════════════════════
#
#  Design principles:
#  1. Patterns are NOT equal — CHoCH/BOS carry more information than Swings
#  2. Confluence is directional — mixed bullish+bearish signals reduce confidence
#  3. Higher TF bias multiplies confidence, not just adds a flat bonus
#  4. Volume is a filter, not a signal on its own
#  5. Result is normalized 1-5 for display
#
# ── Pattern weights (how much raw confidence each pattern contributes)
_PATTERN_WEIGHTS: dict[str, float] = {
    "CHoCH":  1.0,   # Highest — structural shift, hardest to fake
    "BOS":    0.9,   # Strong structural confirmation
    "IFVG":   0.8,   # Filled gap acting as S/R — reliable
    "OB":     0.7,   # Demand/supply zone
    "FVG":    0.6,   # Unfilled gap — good but common
    "Sweeps": 0.6,   # Liquidity sweep — directional
    "Volume": 0.4,   # Amplifier, not a standalone signal
    "PD":     0.4,   # Context only
    "Swings": 0.3,   # Structural reference, too common alone
}

# ── Timeframe weights — higher TF = more reliable signal
_TF_WEIGHT: dict[str, float] = {
    "5m":  0.5,
    "15m": 0.6,
    "30m": 0.7,
    "1h":  0.8,
    "4h":  0.9,
    "1d":  1.0,
}

_TF_HIERARCHY = ["5m", "15m", "30m", "1h", "4h", "1d"]


def _directional_agreement(detected_patterns: dict) -> float:
    """
    Returns a multiplier [0.5 — 1.0] based on how consistently
    all detected patterns agree on direction.

    All bullish or all bearish → 1.0 (full confidence)
    Mixed signals             → 0.5 (halved confidence)
    Neutral/no direction      → 0.75
    """
    bullish_patterns = {"BOS", "CHoCH", "FVG", "IFVG", "OB", "Sweeps"}
    directions = []
    for pname, plist in detected_patterns.items():
        for p in (plist if isinstance(plist, list) else [plist]):
            d = p.get("direction", "") if isinstance(p, dict) else ""
            if d in ("Bullish", "High", "Discount"):
                directions.append("bullish")
            elif d in ("Bearish", "Low", "Premium"):
                directions.append("bearish")

    if not directions:
        return 0.75
    bull = directions.count("bullish")
    bear = directions.count("bearish")
    total = bull + bear
    if total == 0:
        return 0.75
    agreement = max(bull, bear) / total  # 1.0 if all same, 0.5 if split
    return max(0.5, agreement)


def _htf_bias(symbol: str, timeframe: str, pattern_types: set,
              detection_cache: dict) -> float:
    """
    Higher timeframe bias multiplier.

    If the SAME structural patterns (BOS/CHoCH/OB) appear on
    the next 1-2 higher timeframes, return a multiplier > 1.0.
    If HTF shows OPPOSITE direction, penalise (< 1.0).

    Returns multiplier in range [0.7 — 1.3].
    """
    try:
        tf_idx = _TF_HIERARCHY.index(timeframe)
    except ValueError:
        return 1.0

    structural = {"BOS", "CHoCH", "OB", "FVG"}
    current_structural = pattern_types & structural

    if not current_structural:
        return 1.0

    htf_checks = _TF_HIERARCHY[tf_idx + 1: tf_idx + 3]  # next 2 TFs
    if not htf_checks:
        return 1.0

    confirm_score = 0.0
    checks = 0
    for htf in htf_checks:
        htf_cache = detection_cache.get((symbol, htf), {})
        if not htf_cache:
            continue
        checks += 1
        overlap = current_structural & set(htf_cache.keys())
        if overlap:
            confirm_score += 1.0
        else:
            confirm_score -= 0.3  # HTF has no matching structure — slight penalty

    if checks == 0:
        return 1.0

    # Map [-checks, +checks] to [0.7, 1.3]
    ratio = confirm_score / checks
    return 1.0 + (ratio * 0.3)


def score_signal(symbol: str, timeframe: str, patterns: dict,
                 detection_cache: dict) -> int:
    """
    Weighted confidence model. Returns 1-5.

    Steps:
    1. Sum weighted pattern scores
    2. Multiply by TF weight (higher TF = more reliable)
    3. Multiply by directional agreement (mixed signals = lower)
    4. Multiply by HTF bias (HTF confirmation = boost, contradiction = penalty)
    5. Normalize to 1-5 integer scale
    """
    if not patterns:
        return 1

    # 1. Raw pattern score
    raw = sum(_PATTERN_WEIGHTS.get(p, 0.3) for p in patterns)

    # 2. TF weight
    tf_w = _TF_WEIGHT.get(timeframe, 0.6)

    # 3. Directional agreement
    # detection_cache[(symbol, tf)] has full pattern dicts
    full_patterns = detection_cache.get((symbol, timeframe), {})
    dir_agreement = _directional_agreement(full_patterns)

    # 4. HTF bias
    htf_mult = _htf_bias(symbol, timeframe, set(patterns.keys()), detection_cache)

    # 5. Final confidence score
    confidence = raw * tf_w * dir_agreement * htf_mult

    # Normalize: empirical range [0.0 — ~4.0] → [1 — 5]
    # Using thresholds tuned for typical ICT signal density:
    if confidence < 0.4:  return 1   # Weak
    if confidence < 0.8:  return 2   # Moderate
    if confidence < 1.3:  return 3   # Good
    if confidence < 2.0:  return 4   # Strong
    return 5                          # Excellent


def score_to_stars(score: int) -> str:
    filled = "★" * score
    empty  = "☆" * (5 - score)
    labels = {1: "Weak", 2: "Moderate", 3: "Good", 4: "Strong", 5: "Excellent"}
    return f"{filled}{empty} — {labels.get(score, '')}"
