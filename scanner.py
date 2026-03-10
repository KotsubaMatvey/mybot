"""
ICT Scanner v2 — improved pattern detection
Patterns: FVG (unfilled), OB, BOS, CHoCH, Swings, Sweeps, Volume, Premium/Discount
Multi-timeframe confluence detection.
"""

import asyncio
import logging
import aiohttp
from datetime import datetime, timezone
from config import SYMBOLS, TIMEFRAMES, CANDLE_LIMIT

logger = logging.getLogger(__name__)

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
ALL_PATTERNS = ["FVG", "IFVG", "OB", "BOS", "CHoCH", "Swings", "Sweeps", "Volume", "PD", "Breaker", "EQH", "EQL", "SMT"]


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
    except Exception as e:
        logger.error(f"fetch_candles {symbol} {interval}: {type(e).__name__}: {e}")
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
    ICT OB per lecture definition (Month 4, Lesson 3):

    Bullish OB: the LAST bearish candle (close < open) with the LARGEST body
                among consecutive bearish candles immediately before the impulse
                that breaks a swing high. Price must then return to the OB body
                (open/close range, not wicks — ICT: "we focus on the body first").
                Entry zone = ob_close..ob_open (body of the bearish candle).
                SL below ob_low (wick). OB is invalidated if price closes below
                the body midpoint (50% mean threshold).

    Bearish OB: the LAST bullish candle (close > open) with the LARGEST body
                before the impulse that breaks a swing low.
                Entry zone = ob_open..ob_close (body of the bullish candle).

    Confirmation: OB is only valid AFTER the candle that breaks the swing
                  high/low has closed (BOS confirmed on closed candle).

    Alert fires when current price re-enters the OB BODY zone.
    """
    results = []
    if len(candles) < 15:
        return results

    current  = candles[-1]
    # Use closed candles only for structure detection
    lookback = candles[-35:-1]
    n = len(lookback)

    # Find real swing highs and lows using 3-candle structure
    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / n
    min_range = avg_range * 0.3

    last_sh = last_sl = None
    for i in range(n - 2, 0, -1):
        c_prev, c_mid, c_next = lookback[i-1], lookback[i], lookback[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if last_sh is None and c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            last_sh = (i, c_mid["high"])
        if last_sl is None and c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            last_sl = (i, c_mid["low"])
        if last_sh and last_sl:
            break

    # ── Bullish OB: last bearish candle(s) before BOS up (close > swing high)
    if last_sh:
        sh_idx, sh_level = last_sh
        # Find BOS candle — first candle AFTER swing that closes above sh_level
        bos_idx = None
        for i in range(sh_idx + 1, n):
            if lookback[i]["close"] > sh_level:
                bos_idx = i
                break
        if bos_idx is not None and bos_idx > 1:
            # Walk backwards from BOS to find the last consecutive bearish candle
            # ICT: "the last down-close candle with the largest body range"
            best_c = None
            best_body = 0
            # Scan the group of bearish candles immediately before BOS
            for i in range(bos_idx - 1, max(bos_idx - 6, 0), -1):
                c = lookback[i]
                if c["close"] >= c["open"]:
                    break  # stop at first non-bearish candle
                body = c["open"] - c["close"]
                if body > best_body:
                    best_body = body
                    best_c = c
            if best_c is not None:
                # Bearish candle: open = top of body, close = bottom of body
                ob_body_hi = best_c["open"]   # top of body
                ob_body_lo = best_c["close"]  # bottom of body
                midpoint   = (ob_body_hi + ob_body_lo) / 2
                # Price returns into OB body from above
                in_body = ob_body_lo <= current["close"] <= ob_body_hi or \
                          ob_body_lo <= current["low"]   <= ob_body_hi
                # ICT: invalidated if price closes below 50% (mean threshold breached)
                not_violated = current["close"] >= midpoint
                if in_body and not_violated:
                    results.append({
                        "type": "OB", "direction": "Bullish",
                        "ob_high": ob_body_hi, "ob_low": ob_body_lo,
                        "time": best_c["time"],
                        "detail": (f"OB: {ts_utc(best_c['time'])} | "
                                   f"{fmt_price(ob_body_lo)} - {fmt_price(ob_body_hi)} | Bullish OB")
                    })

    # ── Bearish OB: last bullish candle(s) before BOS down (close < swing low)
    if last_sl:
        sl_idx, sl_level = last_sl
        bos_idx = None
        for i in range(sl_idx + 1, n):
            if lookback[i]["close"] < sl_level:
                bos_idx = i
                break
        if bos_idx is not None and bos_idx > 1:
            best_c = None
            best_body = 0
            for i in range(bos_idx - 1, max(bos_idx - 6, 0), -1):
                c = lookback[i]
                if c["close"] <= c["open"]:
                    break
                body = c["close"] - c["open"]
                if body > best_body:
                    best_body = body
                    best_c = c
            if best_c is not None:
                # Bullish candle: open = bottom of body, close = top of body
                ob_body_lo = best_c["open"]
                ob_body_hi = best_c["close"]
                midpoint   = (ob_body_hi + ob_body_lo) / 2
                # Price returns into OB body from below; invalidated if closes above midpoint
                in_body = ob_body_lo <= current["close"] <= ob_body_hi or \
                          ob_body_lo <= current["high"]  <= ob_body_hi
                # ICT: OB valid as long as price hasn't closed back above 50% of the body
                not_violated = current["close"] >= ob_body_lo  # price still touching body, not blown through
                if in_body and not_violated:
                    results.append({
                        "type": "OB", "direction": "Bearish",
                        "ob_high": ob_body_hi, "ob_low": ob_body_lo,
                        "time": best_c["time"],
                        "detail": (f"OB: {ts_utc(best_c['time'])} | "
                                   f"{fmt_price(ob_body_lo)} - {fmt_price(ob_body_hi)} | Bearish OB")
                    })

    return results


# ── Breaker Block ─────────────────────────────────────────────────────────────
def detect_breaker(candles):
    """
    ICT Breaker Block per lecture (Month 4, Lesson 5):

    Bullish Breaker:
      Structure: Low1 → swing high (SH) → Low2 where Low2 < Low1.
      The SH candle (last bullish candle at the swing high between the two lows)
      becomes the Breaker zone once price breaks back up above SH (structure shift).
      Zone = body of that SH candle (open..close of the bullish swing candle).
      Alert fires when price returns INTO that body from above (pullback to breaker).

    Bearish Breaker:
      Structure: High1 → swing low (SL) → High2 where High2 > High1.
      The SL candle (last bearish candle at the swing low between the two highs)
      becomes the Breaker zone once price breaks back down below SL.
      Zone = body of that SL candle.
      Alert fires when price returns INTO that body from below.

    Key difference from OB: Breaker is a FAILED OB that has flipped polarity.
    The zone that previously held as support/resistance has been violated and
    now acts as the opposite (support→resistance, resistance→support).
    """
    results = []
    if len(candles) < 25:
        return results

    current  = candles[-1]
    lookback = candles[-50:-1]
    n = len(lookback)

    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / n
    min_range = avg_range * 0.3

    # Collect all swing highs and lows with their indices
    swings_h = []  # (idx, level)
    swings_l = []
    for i in range(1, n - 1):
        c_prev, c_mid, c_next = lookback[i-1], lookback[i], lookback[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            swings_h.append((i, c_mid["high"]))
        if c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            swings_l.append((i, c_mid["low"]))

    # ── Bullish Breaker: Low1 → SH → Low2 (Low2 < Low1) → BOS up above SH
    # Walk swing lows from recent to older, find pair where second low < first low
    for j in range(len(swings_l) - 1, 0, -1):
        sl2_idx, sl2_level = swings_l[j]      # more recent low
        sl1_idx, sl1_level = swings_l[j - 1]  # older low
        if sl2_idx <= sl1_idx:
            continue
        if sl2_level >= sl1_level:             # need Low2 < Low1
            continue
        # Find swing high between the two lows
        sh_between = [(i, lv) for i, lv in swings_h if sl1_idx < i < sl2_idx]
        if not sh_between:
            continue
        sh_idx, sh_level = sh_between[-1]      # most recent SH between the lows
        # BOS up: any candle after Low2 closes above the SH level
        bos_up_idx = None
        for i in range(sl2_idx + 1, n):
            if lookback[i]["close"] > sh_level:
                bos_up_idx = i
                break
        if bos_up_idx is None:
            continue
        # Breaker = the bullish candle AT or forming the swing high (last up-close candle at SH)
        breaker_c = None
        for i in range(sh_idx, max(sh_idx - 3, 0), -1):
            c = lookback[i]
            if c["close"] > c["open"]:
                breaker_c = c
                break
        if breaker_c is None:
            continue
        # Zone = body of that bullish candle
        bk_lo = breaker_c["open"]
        bk_hi = breaker_c["close"]
        # Alert: price pulls back into breaker body from above
        in_zone = bk_lo <= current["close"] <= bk_hi or bk_lo <= current["low"] <= bk_hi
        if in_zone:
            results.append({
                "type": "Breaker", "direction": "Bullish",
                "ob_high": bk_hi, "ob_low": bk_lo,
                "time": breaker_c["time"],
                "detail": (f"BREAKER: {ts_utc(breaker_c['time'])} | "
                           f"{fmt_price(bk_lo)} - {fmt_price(bk_hi)} | Bullish Breaker")
            })
        break  # only the most recent valid structure

    # ── Bearish Breaker: High1 → SL → High2 (High2 > High1) → BOS down below SL
    for j in range(len(swings_h) - 1, 0, -1):
        sh2_idx, sh2_level = swings_h[j]
        sh1_idx, sh1_level = swings_h[j - 1]
        if sh2_idx <= sh1_idx:
            continue
        if sh2_level <= sh1_level:             # need High2 > High1
            continue
        sl_between = [(i, lv) for i, lv in swings_l if sh1_idx < i < sh2_idx]
        if not sl_between:
            continue
        sl_idx, sl_level = sl_between[-1]
        bos_dn_idx = None
        for i in range(sh2_idx + 1, n):
            if lookback[i]["close"] < sl_level:
                bos_dn_idx = i
                break
        if bos_dn_idx is None:
            continue
        breaker_c = None
        for i in range(sl_idx, max(sl_idx - 3, 0), -1):
            c = lookback[i]
            if c["close"] < c["open"]:
                breaker_c = c
                break
        if breaker_c is None:
            continue
        # Zone = body of that bearish candle
        bk_lo = breaker_c["close"]
        bk_hi = breaker_c["open"]
        # Alert: price pulls back into breaker body from below
        in_zone = bk_lo <= current["close"] <= bk_hi or bk_lo <= current["high"] <= bk_hi
        if in_zone:
            results.append({
                "type": "Breaker", "direction": "Bearish",
                "ob_high": bk_hi, "ob_low": bk_lo,
                "time": breaker_c["time"],
                "detail": (f"BREAKER: {ts_utc(breaker_c['time'])} | "
                           f"{fmt_price(bk_lo)} - {fmt_price(bk_hi)} | Bearish Breaker")
            })
        break

    return results
# ── Equal Highs / Equal Lows (EQH / EQL) ─────────────────────────────────────
def _find_swing_levels(candles):
    """Helper: returns (swing_highs, swing_lows) lists from lookback."""
    lookback  = candles[-50:-1]
    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / len(lookback)
    min_range = avg_range * 0.3
    sh_levels, sl_levels = [], []
    for i in range(1, len(lookback) - 1):
        c_prev, c_mid, c_next = lookback[i-1], lookback[i], lookback[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            sh_levels.append(c_mid["high"])
        if c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            sl_levels.append(c_mid["low"])
    return sh_levels, sl_levels


def detect_eqh(candles):
    """
    Equal Highs (EQH): two or more swing highs within 0.1% of each other.
    Explicit buy-side liquidity pool. Alert when price approaches from below.
    """
    if len(candles) < 20:
        return []
    current = candles[-1]
    sh_levels, _ = _find_swing_levels(candles)
    tolerance = 0.001  # 0.1%

    seen = set()
    for level in sh_levels:
        if level in seen:
            continue
        matches = [l for l in sh_levels if abs(l - level) / level <= tolerance]
        for m in matches:
            seen.add(m)
        if len(matches) >= 2:
            eqh = sum(matches) / len(matches)
            proximity = abs(current["high"] - eqh) / eqh
            if current["high"] <= eqh and proximity <= 0.002:
                return [{
                    "type": "EQH", "direction": "Bearish",
                    "level": eqh, "time": current["time"],
                    "detail": (f"EQH: {ts_utc(current['time'])} | "
                               f"{fmt_price(eqh)} | Equal Highs — BSL above ({len(matches)} touches)")
                }]
    return []


def detect_eql(candles):
    """
    Equal Lows (EQL): two or more swing lows within 0.1% of each other.
    Explicit sell-side liquidity pool. Alert when price approaches from above.
    """
    if len(candles) < 20:
        return []
    current = candles[-1]
    _, sl_levels = _find_swing_levels(candles)
    tolerance = 0.001

    seen = set()
    for level in sl_levels:
        if level in seen:
            continue
        matches = [l for l in sl_levels if abs(l - level) / level <= tolerance]
        for m in matches:
            seen.add(m)
        if len(matches) >= 2:
            eql = sum(matches) / len(matches)
            proximity = abs(current["low"] - eql) / eql
            if current["low"] >= eql and proximity <= 0.002:
                return [{
                    "type": "EQL", "direction": "Bullish",
                    "level": eql, "time": current["time"],
                    "detail": (f"EQL: {ts_utc(current['time'])} | "
                               f"{fmt_price(eql)} | Equal Lows — SSL below ({len(matches)} touches)")
                }]
    return []


# ── BOS (Break of Structure) ──────────────────────────────────────────────────
def detect_bos(candles):
    """
    ICT BOS (Break of Structure): price closes beyond the LAST confirmed swing high/low.

    Bullish BOS: close above last swing high → market shifted bullish.
    Bearish BOS: close below last swing low  → market shifted bearish.

    Uses real 3-candle swing structure.
    lookback[-32:-2] gives swing candidates where the right-neighbour exists in the window.
    """
    if len(candles) < 20:
        return []

    # Use a wider range for finding swings, exclude last 2 candles as they may
    # not have a confirmed right neighbour yet
    scan = candles[-35:]
    lookback = scan[:-2]      # swing detection window
    # BOS requires a CLOSED candle — candles[-1] is still forming
    last     = candles[-2]

    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / len(lookback)
    min_range = avg_range * 0.3

    last_sh = None
    last_sl = None

    # Find the most recent significant swing high and swing low
    for i in range(len(lookback) - 2, 0, -1):
        c_prev, c_mid, c_next = lookback[i-1], lookback[i], lookback[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if last_sh is None and c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            last_sh = c_mid["high"]
        if last_sl is None and c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            last_sl = c_mid["low"]
        if last_sh is not None and last_sl is not None:
            break

    results = []
    if last_sh is not None and last["close"] > last_sh:
        results.append({"type": "BOS", "direction": "Bullish", "level": last_sh,
                        "time": last["time"],
                        "detail": f"BOS: {ts_utc(last['time'])} | {fmt_price(last_sh)} | Bullish BOS"})
    if last_sl is not None and last["close"] < last_sl:
        results.append({"type": "BOS", "direction": "Bearish", "level": last_sl,
                        "time": last["time"],
                        "detail": f"BOS: {ts_utc(last['time'])} | {fmt_price(last_sl)} | Bearish BOS"})
    return results


# ── CHoCH (Change of Character) ───────────────────────────────────────────────
def detect_choch(candles):
    """
    CHoCH: price breaks the LAST swing high/low in the OPPOSITE direction of trend.
    Trend up (higher highs) -> CHoCH when price breaks last swing low.
    Trend down (lower lows) -> CHoCH when price breaks last swing high.
    """
    if len(candles) < 30:
        return []

    # Swing detection must use only CLOSED candles.
    # candles[-1] is still forming — its high/low can change.
    # Use candles[:-1] for swing structure, candles[-2] for BOS confirmation.
    closed = candles[:-1]
    swing_highs = []
    swing_lows = []
    for i in range(1, len(closed) - 1):
        c = closed[i]
        if c["high"] > closed[i-1]["high"] and c["high"] > closed[i+1]["high"]:
            swing_highs.append(c["high"])
        if c["low"] < closed[i-1]["low"] and c["low"] < closed[i+1]["low"]:
            swing_lows.append(c["low"])

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return []

    # CHoCH requires a CLOSED candle — candles[-1] is still forming
    last = candles[-2]
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
    """
    ICT Swing High: 3-candle pattern — middle candle has higher high than both neighbours.
    ICT Swing Low:  3-candle pattern — middle candle has lower low than both neighbours.
    Color of candles is irrelevant.

    Significance filter: the swing candle body must be >= 30% of the average candle
    range over the lookback period. This eliminates doji/noise swings.
    Only the most recent significant swing is reported.
    """
    if len(candles) < 10:
        return []

    # Exclude candles[-1] — it's still forming. A swing high/low requires
    # the right-neighbour (third candle) to be CLOSED to confirm the pattern.
    lookback = candles[-31:-1]  # all closed candles
    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / len(lookback)
    min_range = avg_range * 0.3  # swing candle must be meaningful

    # Scan from newest to oldest. At i = len-2: c_mid = lookback[-2], c_next = lookback[-1]
    # Both are confirmed closed candles.
    for i in range(len(lookback) - 2, 0, -1):
        c_prev = lookback[i - 1]
        c_mid  = lookback[i]
        c_next = lookback[i + 1]
        candle_range = c_mid["high"] - c_mid["low"]

        if candle_range < min_range:
            continue  # noise candle, skip

        if c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            return [{"type": "Swings", "direction": "High", "level": c_mid["high"],
                     "time": c_mid["time"],
                     "detail": f"SWING: {ts_utc(c_mid['time'])} | {fmt_price(c_mid['high'])} | Swing High"}]

        if c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            return [{"type": "Swings", "direction": "Low", "level": c_mid["low"],
                     "time": c_mid["time"],
                     "detail": f"SWING: {ts_utc(c_mid['time'])} | {fmt_price(c_mid['low'])} | Swing Low"}]

    return []


# ── Sweeps (Liquidity Sweeps) ─────────────────────────────────────────────────
def detect_sweeps(candles):
    """
    ICT Liquidity Sweep: price wicks above a real swing high (or below swing low)
    but CLOSES back on the other side. This is the turtle soup / false breakout.

    CRITICAL: sweep is confirmed only on a CLOSED candle.
    We use candles[-2] — the last fully closed candle.
    candles[-1] is the current forming candle — never use it for sweep confirmation.

    Swing levels are built from candles[-31:-2] (all closed, excluding the sweep candle itself).
    We use the most RECENT swing high/low, not the highest/lowest — that's what gets swept.
    """
    if len(candles) < 25:
        return []

    # Last CLOSED candle — this is the sweep candle we are confirming
    closed = candles[-2]
    # Build swings from candles before the sweep candle
    lookback = candles[-31:-2]
    if len(lookback) < 5:
        return []

    avg_range = sum(abs(c["high"] - c["low"]) for c in lookback) / len(lookback)
    min_range = avg_range * 0.3

    # Collect real swing highs and lows with their index (newest last)
    swing_highs = []  # list of (index, level)
    swing_lows  = []
    for i in range(1, len(lookback) - 1):
        c_prev, c_mid, c_next = lookback[i-1], lookback[i], lookback[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            swing_highs.append((i, c_mid["high"]))
        if c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            swing_lows.append((i, c_mid["low"]))

    results = []

    # Most recent swing high = last in list (highest index)
    if swing_highs:
        _, recent_sh = swing_highs[-1]
        # Sweep: wick above swing high BUT close back below it
        if closed["high"] > recent_sh and closed["close"] < recent_sh:
            results.append({
                "type": "Sweeps", "direction": "Bearish", "level": recent_sh,
                "time": closed["time"],
                "detail": f"SWEEP: {ts_utc(closed['time'])} | {fmt_price(recent_sh)} | Bearish Sweep"
            })

    # Most recent swing low
    if swing_lows:
        _, recent_sl = swing_lows[-1]
        # Sweep: wick below swing low BUT close back above it
        if closed["low"] < recent_sl and closed["close"] > recent_sl:
            results.append({
                "type": "Sweeps", "direction": "Bullish", "level": recent_sl,
                "time": closed["time"],
                "detail": f"SWEEP: {ts_utc(closed['time'])} | {fmt_price(recent_sl)} | Bullish Sweep"
            })

    return results


# ── Volume ────────────────────────────────────────────────────────────────────
def detect_volume(candles):
    """
    Significant volume spike: current candle volume > 2.0x the 20-candle average.
    3% threshold (old code) is background noise. 2x is the first meaningful level.
    Shows tier: Notable (2x), Elevated (3x), Extreme (5x+).
    """
    if len(candles) < 22:
        return []
    # Volume spike confirmed only on a CLOSED candle
    last = candles[-2]
    avg_vol = sum(c["volume"] for c in candles[-22:-2]) / 20
    if avg_vol == 0:
        return []

    ratio = last["volume"] / avg_vol
    if ratio < 2.0:
        return []  # not significant

    pct = (ratio - 1) * 100
    usd_vol = last["volume"] * last["close"]
    usd_str = f"${usd_vol/1_000_000:.1f}M" if usd_vol >= 1_000_000 else f"${usd_vol/1_000:.0f}K"

    if ratio >= 5.0:
        tier = "Extreme"
    elif ratio >= 3.0:
        tier = "Elevated"
    else:
        tier = "Notable"

    direction = "Bullish" if last["close"] >= last["open"] else "Bearish"
    detail = (f"VOLUME: {ts_utc(last['time'])} | {usd_str} | "
              f"+{pct:.0f}% avg | {tier} {direction}")
    return [{"type": "Volume", "direction": direction,
             "level": last["volume"], "time": last["time"], "detail": detail}]


# ── Premium / Discount / OTE Zones ───────────────────────────────────────────
def detect_pd_zones(candles):
    """
    ICT Premium/Discount based on last significant swing range.

    Equilibrium = 50% of the range between last swing high and last swing low.
    OTE (Optimal Trade Entry) = 61.8% - 78.6% retracement — high-probability entry zone.

    Bullish context: last swing low below last swing high, price retracing into discount OTE.
    Bearish context: last swing high above last swing low, price retracing into premium OTE.
    """
    if len(candles) < 30:
        return []

    scan     = candles[-51:-1]  # closed candles only — swing detection requires confirmed right-neighbour
    current  = candles[-1]
    avg_range = sum(abs(c["high"] - c["low"]) for c in scan) / len(scan)
    min_range = avg_range * 0.3

    # Find last significant swing high and swing low
    last_sh_val = last_sh_idx = None
    last_sl_val = last_sl_idx = None

    for i in range(len(scan) - 2, 0, -1):
        c_prev, c_mid, c_next = scan[i-1], scan[i], scan[i+1]
        if (c_mid["high"] - c_mid["low"]) < min_range:
            continue
        if last_sh_val is None and c_mid["high"] > c_prev["high"] and c_mid["high"] > c_next["high"]:
            last_sh_val = c_mid["high"]
            last_sh_idx = i
        if last_sl_val is None and c_mid["low"] < c_prev["low"] and c_mid["low"] < c_next["low"]:
            last_sl_val = c_mid["low"]
            last_sl_idx = i
        if last_sh_val is not None and last_sl_val is not None:
            break

    if last_sh_val is None or last_sl_val is None:
        return []

    hi = last_sh_val
    lo = last_sl_val
    eq = (hi + lo) / 2

    # OTE for BULLISH context: swing low formed AFTER swing high (downtrend, now retracing up)
    # Price should be below equilibrium for a buy setup
    # Retracement of a DOWN leg (hi → lo): OTE bounce = 61.8-78.6% of (hi-lo) from lo
    # Retracement of an UP leg  (lo → hi): OTE pullback = 61.8-78.6% of (hi-lo) from hi

    results = []

    # Bullish OTE: swing low was more recent than swing high → price retracing UP into OTE
    if last_sl_idx > last_sh_idx:
        # Down leg from hi to lo; now looking for bounce
        ote_lo = lo + (hi - lo) * 0.618   # 61.8% bounce level
        ote_hi = lo + (hi - lo) * 0.786   # 78.6% bounce level
        in_ote_now  = ote_lo <= current["high"] <= ote_hi
        in_ote_prev = ote_lo <= prev["high"]    <= ote_hi
        if in_ote_now and not in_ote_prev:
            results.append({
                "type": "PD", "direction": "Discount",
                "level": eq, "time": current["time"],
                "detail": (f"OTE ZONE: {ts_utc(current['time'])} | "
                           f"{fmt_price(ote_lo)} - {fmt_price(ote_hi)} | "
                           f"Bullish OTE — buy area (61.8-78.6% retrace)")
            })

    # Bearish OTE: swing high was more recent than swing low → price retracing DOWN into OTE
    elif last_sh_idx > last_sl_idx:
        # Up leg from lo to hi; now looking for pullback
        ote_hi = hi - (hi - lo) * 0.618   # 61.8% pullback level
        ote_lo = hi - (hi - lo) * 0.786   # 78.6% pullback level
        in_ote_now  = ote_lo <= current["low"] <= ote_hi
        in_ote_prev = ote_lo <= prev["low"]    <= ote_hi
        if in_ote_now and not in_ote_prev:
            results.append({
                "type": "PD", "direction": "Premium",
                "level": eq, "time": current["time"],
                "detail": (f"OTE ZONE: {ts_utc(current['time'])} | "
                           f"{fmt_price(ote_lo)} - {fmt_price(ote_hi)} | "
                           f"Bearish OTE — sell area (61.8-78.6% retrace)")
            })

    # Fallback: equilibrium cross (weaker signal, context only)
    if not results:
        if prev["close"] <= eq < current["close"]:
            results.append({"type": "PD", "direction": "Premium",
                             "level": eq, "time": current["time"],
                             "detail": f"PREMIUM: {ts_utc(current['time'])} | EQ {fmt_price(eq)} | Above equilibrium"})
        elif prev["close"] >= eq > current["close"]:
            results.append({"type": "PD", "direction": "Discount",
                             "level": eq, "time": current["time"],
                             "detail": f"DISCOUNT: {ts_utc(current['time'])} | EQ {fmt_price(eq)} | Below equilibrium"})

    return results


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


# ── SMT Divergence ────────────────────────────────────────────────────────────
# Only meaningful on 1h, 4h, 1d — lower TF has too much noise.
SMT_TIMEFRAMES = {"1h", "4h", "1d"}
# SMT pairs: for each "primary" symbol, which symbol should confirm it?
# Both must be in SYMBOLS for SMT to fire.
SMT_PAIRS = [("BTCUSDT", "ETHUSDT")]

def detect_smt(candles_a: list, candles_b: list, sym_a: str, sym_b: str) -> list:
    """
    ICT SMT Divergence per lecture (Month 3, Lesson 5 + Market Maker Series Vol.3):

    Bearish SMT:
      sym_a makes a Higher High (new swing high above previous swing high).
      sym_b at the SAME TIME makes a Lower High (fails to confirm).
      Broken correlation = smart money distributing. Expect reversal down.

    Bullish SMT:
      sym_a makes a Lower Low (new swing low below previous swing low).
      sym_b at the SAME TIME makes a Higher Low (fails to confirm).
      Broken correlation = smart money accumulating. Expect reversal up.

    Both candle arrays must be time-aligned (same exchange, same interval).
    We compare the two most recent completed swing structures.
    """
    results = []
    if len(candles_a) < 10 or len(candles_b) < 10:
        return results

    # Use last 40 closed candles for swing detection
    ca = candles_a[-41:-1]
    cb = candles_b[-41:-1]
    n = min(len(ca), len(cb))
    if n < 10:
        return results

    # Align by timestamp: only compare candles where both have the same open time
    # Build index: time → candle for sym_b
    cb_by_time = {c["time"]: c for c in cb}
    aligned_a = []
    aligned_b = []
    for c in ca:
        if c["time"] in cb_by_time:
            aligned_a.append(c)
            aligned_b.append(cb_by_time[c["time"]])

    n = len(aligned_a)
    if n < 10:
        return results

    avg_range_a = sum(abs(c["high"] - c["low"]) for c in aligned_a) / n
    min_range_a = avg_range_a * 0.3

    # Find swing highs and lows in sym_a (primary asset)
    sh_a = []  # (idx, high_level)
    sl_a = []  # (idx, low_level)
    for i in range(1, n - 1):
        ca_prev, ca_mid, ca_next = aligned_a[i-1], aligned_a[i], aligned_a[i+1]
        if (ca_mid["high"] - ca_mid["low"]) < min_range_a:
            continue
        if ca_mid["high"] > ca_prev["high"] and ca_mid["high"] > ca_next["high"]:
            sh_a.append((i, ca_mid["high"]))
        if ca_mid["low"] < ca_prev["low"] and ca_mid["low"] < ca_next["low"]:
            sl_a.append((i, ca_mid["low"]))

    if len(sh_a) < 2 and len(sl_a) < 2:
        return results

    current_a = candles_a[-1]
    current_b = candles_b[-1]

    # ── Bearish SMT: sym_a HH, sym_b LH at corresponding swing
    if len(sh_a) >= 2:
        # Two most recent swing highs in sym_a
        sh2_idx, sh2_lv = sh_a[-1]   # more recent
        sh1_idx, sh1_lv = sh_a[-2]   # older
        if sh2_lv > sh1_lv:          # sym_a made HH
            # What did sym_b do at the same candle index?
            b_at_sh1 = aligned_b[sh1_idx]["high"]
            b_at_sh2 = aligned_b[sh2_idx]["high"]
            if b_at_sh2 < b_at_sh1:  # sym_b made LH — divergence confirmed
                # Alert only when current price is near or below the swing high
                # (we don't want to alert 50 candles later)
                candles_since = n - 1 - sh2_idx
                if candles_since <= 8:  # signal must be recent
                    results.append({
                        "type":      "SMT",
                        "direction": "Bearish",
                        "time":      aligned_a[sh2_idx]["time"],
                        "level":     sh2_lv,
                        "detail": (
                            f"SMT Bearish: {sym_a} HH {fmt_price(sh2_lv)} "
                            f"/ {sym_b} LH {fmt_price(b_at_sh2)} — divergence"
                        ),
                    })

    # ── Bullish SMT: sym_a LL, sym_b HL at corresponding swing
    if len(sl_a) >= 2:
        sl2_idx, sl2_lv = sl_a[-1]
        sl1_idx, sl1_lv = sl_a[-2]
        if sl2_lv < sl1_lv:          # sym_a made LL
            b_at_sl1 = aligned_b[sl1_idx]["low"]
            b_at_sl2 = aligned_b[sl2_idx]["low"]
            if b_at_sl2 > b_at_sl1:  # sym_b made HL — divergence confirmed
                candles_since = n - 1 - sl2_idx
                if candles_since <= 8:
                    results.append({
                        "type":      "SMT",
                        "direction": "Bullish",
                        "time":      aligned_a[sl2_idx]["time"],
                        "level":     sl2_lv,
                        "detail": (
                            f"SMT Bullish: {sym_a} LL {fmt_price(sl2_lv)} "
                            f"/ {sym_b} HL {fmt_price(b_at_sl2)} — divergence"
                        ),
                    })

    return results


DETECTORS = {
    "FVG":     detect_fvg,
    "IFVG":    detect_ifvg,
    "OB":      detect_ob,
    "Breaker": detect_breaker,
    "EQH":     detect_eqh,
    "EQL":     detect_eql,
    "BOS":     detect_bos,
    "CHoCH":   detect_choch,
    "Swings":  detect_swings,
    "Sweeps":  detect_sweeps,
    "Volume":  detect_volume,
    "PD":      detect_pd_zones,
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

    # ── 2b. SMT Divergence — cross-symbol, only on SMT_TIMEFRAMES
    for sym_a, sym_b in SMT_PAIRS:
        if sym_a not in SYMBOLS or sym_b not in SYMBOLS:
            continue
        for tf in TIMEFRAMES:
            if tf not in SMT_TIMEFRAMES:
                continue
            ca = all_candles.get((sym_a, tf))
            cb = all_candles.get((sym_b, tf))
            if not ca or not cb:
                continue
            try:
                smt_hits = detect_smt(ca, cb, sym_a, sym_b)
            except Exception:
                smt_hits = []
            for p in smt_hits:
                # SMT alert is reported under the PRIMARY symbol (sym_a = BTC)
                if not is_dup(sym_a, tf, "SMT", p):
                    all_alerts.append({
                        "symbol":    sym_a,
                        "timeframe": tf,
                        "pattern":   "SMT",
                        "detail":    p["detail"],
                        "direction": p.get("direction", ""),
                        "score":     None,
                        "gap_low":   None,
                        "gap_high":  None,
                        "ob_low":    None,
                        "ob_high":   None,
                        "level":     p.get("level"),
                        "time":      p.get("time", 0),
                    })
                # Also store in detection_cache so scoring can see it
                detection_cache.setdefault((sym_a, tf), {}).setdefault("SMT", []).append(p)


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
                        "score":     None,
                        # price level fields for chart rendering
                        "gap_low":   p.get("gap_low"),
                        "gap_high":  p.get("gap_high"),
                        "ob_low":    p.get("ob_low"),
                        "ob_high":   p.get("ob_high"),
                        "level":     p.get("level"),
                        "time":      p.get("time", 0),
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
    "CHoCH":   1.0,   # Highest — structural shift, hardest to fake
    "BOS":     0.9,   # Strong structural confirmation
    "SMT":     0.9,   # Cross-asset divergence — high conviction signal
    "IFVG":    0.8,   # Filled gap acting as S/R — reliable
    "Breaker": 0.8,   # Failed OB flipped — high confluence setup
    "OB":      0.7,   # Demand/supply zone, confirmed on return
    "EQH":     0.7,   # Equal highs = explicit liquidity target
    "EQL":     0.7,   # Equal lows = explicit liquidity target
    "FVG":     0.6,   # Unfilled gap — good but common
    "Sweeps":  0.6,   # Liquidity sweep — directional
    "Volume":  0.4,   # Amplifier, not a standalone signal
    "PD":      0.4,   # Context only
    "Swings":  0.3,   # Structural reference, too common alone
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
