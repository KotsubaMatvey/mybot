"""
Scanner orchestration layer.

Layer A: market primitives
Layer B: entry-model strategies
Layer C: alert-friendly dictionaries, caches, chart payloads
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import aiohttp

from config import CANDLE_LIMIT, SYMBOLS, TIMEFRAMES
from market_primitives import (
    BreakerBlock,
    FairValueGap,
    InvertedFVG,
    LiquiditySweep,
    OrderBlock,
    StructureBreak,
    SwingPoint,
    active_fvgs,
    cluster_levels,
    collect_swings,
    detect_breaker_blocks,
    detect_fvg as primitive_detect_fvg,
    detect_ifvg as primitive_detect_ifvg,
    detect_liquidity_raids as primitive_detect_liquidity_raids,
    detect_order_blocks,
    detect_structure_breaks,
    detect_swings as primitive_detect_swings,
    detect_sweeps as primitive_detect_sweeps,
    fmt_price,
    ts_utc,
)
from strategies import (
    PrimitiveSnapshot,
    StrategyContext,
    detect_entry_model_1,
    detect_entry_model_2,
    detect_entry_model_3,
    setup_to_alert,
)

logger = logging.getLogger(__name__)

BINANCE_BASE = "https://fapi.binance.com"

PRIMITIVE_PATTERNS = [
    "FVG",
    "IFVG",
    "OB",
    "BOS",
    "CHoCH",
    "Swings",
    "Sweeps",
    "Liquidity",
    "Volume",
    "VP",
    "KL",
    "PD",
    "Breaker",
    "EQH",
    "EQL",
    "SMT",
]
STRATEGY_PATTERNS = ["Entry Model 1", "Entry Model 2", "Entry Model 3"]
ALL_PATTERNS = PRIMITIVE_PATTERNS + STRATEGY_PATTERNS

MODEL_3_LTF_MAP = {
    "5m": "1m",
    "15m": "5m",
    "30m": "15m",
    "1h": "15m",
    "4h": "1h",
    "1d": "4h",
}
MODEL_3_HTF_MAP = {
    "5m": "15m",
    "15m": "30m",
    "30m": "1h",
    "1h": "4h",
    "4h": "1d",
    "1d": None,
}
SMT_TIMEFRAMES = {"1h", "4h", "1d"}
SMT_PAIRS = [("BTCUSDT", "ETHUSDT")]

_candle_cache: dict[tuple[str, str], list] = {}
_pattern_cache: dict[tuple[str, str], list] = {}
_active_zones: dict[str, dict[str, list]] = {}
_sent: dict[tuple[Any, ...], bool] = {}
_sem = asyncio.Semaphore(5)


def get_cached_candles(symbol: str, tf: str) -> list:
    return _candle_cache.get((symbol, tf), [])


def get_cached_patterns(symbol: str, tf: str) -> list:
    return _pattern_cache.get((symbol, tf), [])


def get_active_zones() -> dict:
    return dict(_active_zones)


async def fetch_candles(session: aiohttp.ClientSession, symbol: str, interval: str, limit: int = CANDLE_LIMIT) -> list[dict]:
    url = f"{BINANCE_BASE}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
        return [
            {
                "time": int(c[0]),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            }
            for c in data
        ]
    except Exception as exc:
        logger.error("fetch_candles %s %s: %s: %s", symbol, interval, type(exc).__name__, exc)
        return []


async def _fetch_with_sem(session: aiohttp.ClientSession, symbol: str, tf: str) -> list[dict]:
    async with _sem:
        return await fetch_candles(session, symbol, tf)


def _price_bucket(price: float) -> int:
    if price <= 0:
        return 0
    return int(price / (price * 0.005))


def is_dup(symbol: str, tf: str, ptype: str, pattern: dict) -> bool:
    direction = pattern.get("direction", "")
    ts = pattern.get("time", 0)
    level = (
        pattern.get("entry_low")
        or pattern.get("gap_low")
        or pattern.get("ob_low")
        or pattern.get("level")
        or 0
    )
    key = (symbol, tf, ptype, direction, _price_bucket(float(level)), ts)
    if key in _sent:
        return True
    _sent[key] = True
    if len(_sent) > 5000:
        for old_key in list(_sent.keys())[:500]:
            del _sent[old_key]
    return False


def _snapshot_for(symbol: str, timeframe: str, candles: list[dict]) -> PrimitiveSnapshot:
    swings = primitive_detect_swings(candles, symbol, timeframe)
    sweeps = primitive_detect_sweeps(candles, symbol, timeframe)
    raids = primitive_detect_liquidity_raids(candles, symbol, timeframe)
    structure_breaks = detect_structure_breaks(candles, symbol, timeframe)
    fvgs = primitive_detect_fvg(candles, symbol, timeframe)
    ifvgs = primitive_detect_ifvg(candles, symbol, timeframe)
    order_blocks = detect_order_blocks(candles, symbol, timeframe)
    breaker_blocks = detect_breaker_blocks(candles, symbol, timeframe)
    key_levels = [item["level"] for item in detect_key_levels(candles)]
    return PrimitiveSnapshot(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        swings=swings,
        sweeps=sweeps,
        raids=raids,
        structure_breaks=structure_breaks,
        fvgs=fvgs,
        ifvgs=ifvgs,
        order_blocks=order_blocks,
        breaker_blocks=breaker_blocks,
        key_levels=key_levels,
    )


def _primitive_alerts(snapshot: PrimitiveSnapshot) -> list[dict]:
    alerts: list[dict] = []

    for swing in snapshot.swings:
        alerts.append(_swing_to_alert(swing))
    for sweep in snapshot.sweeps:
        alerts.append(_sweep_to_alert(sweep, "Sweeps"))
    for raid in snapshot.raids:
        alerts.append(_sweep_to_alert(raid, "Liquidity"))
    for structure in snapshot.structure_breaks:
        alerts.append(_structure_to_alert(structure))
    for fvg in [item for item in snapshot.fvgs if not item.invalidated][-2:]:
        alerts.append(_fvg_to_alert(fvg, "FVG"))
    for ifvg in snapshot.ifvgs[-2:]:
        alerts.append(_ifvg_to_alert(ifvg))
    for block in snapshot.order_blocks:
        alerts.append(_order_block_to_alert(block))
    for breaker in snapshot.breaker_blocks:
        alerts.append(_breaker_to_alert(breaker))

    alerts.extend(_retag_alerts(detect_volume(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    alerts.extend(_retag_alerts(detect_volume_profile(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    alerts.extend(_retag_alerts(detect_key_levels(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    alerts.extend(_retag_alerts(detect_pd_zones(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    alerts.extend(_retag_alerts(detect_eqh(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    alerts.extend(_retag_alerts(detect_eql(snapshot.candles), snapshot.symbol, snapshot.timeframe))
    return alerts


def _strategy_alerts(
    primary: PrimitiveSnapshot,
    higher: PrimitiveSnapshot | None,
    lower: PrimitiveSnapshot | None,
) -> list[dict]:
    context = StrategyContext(primary=primary, higher_timeframe=higher, lower_timeframe=lower)
    setups = []
    setups.extend(detect_entry_model_1(context))
    setups.extend(detect_entry_model_2(context))
    setups.extend(detect_entry_model_3(context))
    deduped: dict[tuple[str, str], dict] = {}
    for setup in setups:
        key = (setup.model_name, setup.direction)
        existing = deduped.get(key)
        if existing is None or setup.score > existing["setup"].score:
            deduped[key] = setup_to_alert(setup)
    return list(deduped.values())


async def run_scanner() -> tuple[list, list, dict]:
    all_alerts: list[dict] = []
    fetch_timeframes = sorted(set(TIMEFRAMES) | {tf for tf in MODEL_3_LTF_MAP.values() if tf})

    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        combos = [(symbol, tf) for symbol in SYMBOLS for tf in fetch_timeframes]
        tasks = [_fetch_with_sem(session, symbol, tf) for symbol, tf in combos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_candles: dict[tuple[str, str], list] = {}
    for (symbol, tf), candles in zip(combos, results):
        if isinstance(candles, Exception) or not candles:
            continue
        all_candles[(symbol, tf)] = candles
        _candle_cache[(symbol, tf)] = candles

    primitive_cache: dict[tuple[str, str], PrimitiveSnapshot] = {}
    for (symbol, tf), candles in all_candles.items():
        primitive_cache[(symbol, tf)] = _snapshot_for(symbol, tf, candles)

    global _active_zones
    _active_zones = {}
    by_symbol: dict[str, dict[str, list]] = {symbol: {} for symbol in SYMBOLS}

    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            primary = primitive_cache.get((symbol, tf))
            if primary is None:
                continue

            primitive_alerts = _primitive_alerts(primary)
            higher_tf = MODEL_3_HTF_MAP.get(tf)
            lower_tf = MODEL_3_LTF_MAP.get(tf)
            strategy_alerts = _strategy_alerts(
                primary,
                primitive_cache.get((symbol, higher_tf)) if higher_tf else None,
                primitive_cache.get((symbol, lower_tf)) if lower_tf else None,
            )
            combined = primitive_alerts + strategy_alerts
            if not combined:
                continue

            by_symbol[symbol][tf] = combined
            _active_zones.setdefault(symbol, {})[tf] = combined
            for alert in combined:
                if not is_dup(symbol, tf, alert["pattern"], alert):
                    all_alerts.append(alert)

    for sym_a, sym_b in SMT_PAIRS:
        if sym_a not in SYMBOLS or sym_b not in SYMBOLS:
            continue
        for tf in TIMEFRAMES:
            if tf not in SMT_TIMEFRAMES:
                continue
            candles_a = all_candles.get((sym_a, tf))
            candles_b = all_candles.get((sym_b, tf))
            if not candles_a or not candles_b:
                continue
            for hit in detect_smt(candles_a, candles_b, sym_a, sym_b):
                hit["timeframe"] = tf
                if not is_dup(sym_a, tf, "SMT", hit):
                    all_alerts.append(hit)
                _active_zones.setdefault(sym_a, {}).setdefault(tf, []).append(hit)
                by_symbol.setdefault(sym_a, {}).setdefault(tf, []).append(hit)

    grouped_patterns: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    grouped_alerts: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for alert in all_alerts:
        if alert.get("alert_kind") == "strategy":
            continue
        key = (alert["symbol"], alert["timeframe"])
        grouped_patterns[key][alert["pattern"]] = alert["detail"]
        grouped_alerts[key].append(alert)

    for key, patterns in grouped_patterns.items():
        symbol, tf = key
        score = score_signal(symbol, tf, patterns, primitive_cache)
        for alert in grouped_alerts[key]:
            if alert.get("alert_kind") != "strategy":
                alert["score"] = score

    all_confluences = []
    for symbol, tf_data in by_symbol.items():
        if len(tf_data) >= 2:
            for message in check_confluence(symbol, tf_data):
                all_confluences.append({"symbol": symbol, "message": message})

    _pattern_cache.clear()
    for alert in all_alerts:
        _pattern_cache.setdefault((alert["symbol"], alert["timeframe"]), []).append(alert)

    return all_alerts, all_confluences, all_candles


def _swing_to_alert(swing: SwingPoint) -> dict:
    label = "Swing High" if swing.direction == "high" else "Swing Low"
    direction = "Bearish" if swing.direction == "high" else "Bullish"
    return {
        "symbol": swing.symbol,
        "timeframe": swing.timeframe,
        "pattern": "Swings",
        "type": "Swings",
        "detail": f"SWING: {ts_utc(swing.timestamp)} | {fmt_price(swing.level)} | {label}",
        "direction": direction,
        "score": None,
        "level": swing.level,
        "time": swing.timestamp,
        "alert_kind": "primitive",
    }


def _sweep_to_alert(sweep: LiquiditySweep, pattern_name: str) -> dict:
    direction = "Bullish" if sweep.direction == "bullish" else "Bearish"
    label = "SSL taken and reclaimed" if sweep.direction == "bullish" else "BSL taken and reclaimed"
    prefix = "LIQUIDITY RAID" if pattern_name == "Liquidity" else "SWEEP"
    return {
        "symbol": sweep.symbol,
        "timeframe": sweep.timeframe,
        "pattern": pattern_name,
        "type": pattern_name,
        "detail": f"{prefix}: {ts_utc(sweep.timestamp)} | {fmt_price(sweep.liquidity_level)} | {direction} {label}",
        "direction": direction,
        "score": None,
        "level": sweep.liquidity_level,
        "time": sweep.timestamp,
        "sweep_level": sweep.liquidity_level,
        "alert_kind": "primitive",
    }


def _structure_to_alert(structure: StructureBreak) -> dict:
    direction = "Bullish" if structure.direction == "bullish" else "Bearish"
    pattern_name = "CHoCH" if structure.break_type == "CHOCH" else structure.break_type
    return {
        "symbol": structure.symbol,
        "timeframe": structure.timeframe,
        "pattern": pattern_name,
        "type": pattern_name,
        "detail": f"{pattern_name}: {ts_utc(structure.timestamp)} | {fmt_price(structure.broken_level)} | {direction} {pattern_name}",
        "direction": direction,
        "score": None,
        "level": structure.broken_level,
        "time": structure.timestamp,
        "structure_level": structure.broken_level,
        "alert_kind": "primitive",
    }


def _fvg_to_alert(fvg: FairValueGap, pattern_name: str) -> dict:
    direction = "Bullish" if fvg.direction == "bullish" else "Bearish"
    suffix = "[ACTIVE]" if not fvg.mitigated else "[RETESTED]"
    return {
        "symbol": fvg.symbol,
        "timeframe": fvg.timeframe,
        "pattern": pattern_name,
        "type": pattern_name,
        "detail": f"{pattern_name}: {ts_utc(fvg.created_at)} | {fmt_price(fvg.gap_low)} - {fmt_price(fvg.gap_high)} | {direction} {suffix}",
        "direction": direction,
        "score": None,
        "gap_low": fvg.gap_low,
        "gap_high": fvg.gap_high,
        "time": fvg.mitigated_at or fvg.created_at,
        "alert_kind": "primitive",
    }


def _ifvg_to_alert(ifvg: InvertedFVG) -> dict:
    direction = "Bullish" if ifvg.direction == "bullish" else "Bearish"
    return {
        "symbol": ifvg.symbol,
        "timeframe": ifvg.timeframe,
        "pattern": "IFVG",
        "type": "IFVG",
        "detail": f"IFVG: {ts_utc(ifvg.timestamp)} | {fmt_price(ifvg.zone_low)} - {fmt_price(ifvg.zone_high)} | {direction} inversion retest",
        "direction": direction,
        "score": None,
        "gap_low": ifvg.zone_low,
        "gap_high": ifvg.zone_high,
        "time": ifvg.timestamp,
        "alert_kind": "primitive",
    }


def _order_block_to_alert(block: OrderBlock) -> dict:
    direction = "Bullish" if block.direction == "bullish" else "Bearish"
    return {
        "symbol": block.symbol,
        "timeframe": block.timeframe,
        "pattern": "OB",
        "type": "OB",
        "detail": f"OB: {ts_utc(block.origin_time)} | {fmt_price(block.zone_low)} - {fmt_price(block.zone_high)} | {direction} Order Block",
        "direction": direction,
        "score": None,
        "ob_low": block.zone_low,
        "ob_high": block.zone_high,
        "time": block.timestamp,
        "alert_kind": "primitive",
    }


def _breaker_to_alert(block: BreakerBlock) -> dict:
    direction = "Bullish" if block.direction == "bullish" else "Bearish"
    return {
        "symbol": block.symbol,
        "timeframe": block.timeframe,
        "pattern": "Breaker",
        "type": "Breaker",
        "detail": f"BREAKER: {ts_utc(block.origin_time)} | {fmt_price(block.zone_low)} - {fmt_price(block.zone_high)} | {direction} Breaker",
        "direction": direction,
        "score": None,
        "ob_low": block.zone_low,
        "ob_high": block.zone_high,
        "time": block.timestamp,
        "alert_kind": "primitive",
    }


def _retag_alerts(alerts: list[dict], symbol: str, timeframe: str) -> list[dict]:
    for alert in alerts:
        alert["symbol"] = symbol
        alert["timeframe"] = timeframe
        alert.setdefault("type", alert.get("pattern"))
    return alerts


def _find_swing_levels(candles: list[dict]) -> tuple[list[float], list[float]]:
    swing_highs, swing_lows = collect_swings(candles[-50:-1], "_", "_")
    return [item.level for item in swing_highs], [item.level for item in swing_lows]


def detect_eqh(candles: list[dict]) -> list[dict]:
    if len(candles) < 20:
        return []
    current = candles[-1]
    swing_highs, _ = _find_swing_levels(candles)
    tolerance = 0.001
    seen = set()
    for level in swing_highs:
        if level in seen:
            continue
        matches = [other for other in swing_highs if abs(other - level) / level <= tolerance]
        seen.update(matches)
        if len(matches) >= 2:
            eqh = sum(matches) / len(matches)
            proximity = abs(current["high"] - eqh) / eqh
            if current["high"] <= eqh and proximity <= 0.002:
                return [{
                    "symbol": "_",
                    "timeframe": "_",
                    "pattern": "EQH",
                    "type": "EQH",
                    "detail": f"EQH: {ts_utc(current['time'])} | {fmt_price(eqh)} | Equal Highs - BSL above ({len(matches)} touches)",
                    "direction": "Bearish",
                    "score": None,
                    "level": eqh,
                    "time": current["time"],
                    "alert_kind": "primitive",
                }]
    return []


def detect_eql(candles: list[dict]) -> list[dict]:
    if len(candles) < 20:
        return []
    current = candles[-1]
    _, swing_lows = _find_swing_levels(candles)
    tolerance = 0.001
    seen = set()
    for level in swing_lows:
        if level in seen:
            continue
        matches = [other for other in swing_lows if abs(other - level) / level <= tolerance]
        seen.update(matches)
        if len(matches) >= 2:
            eql = sum(matches) / len(matches)
            proximity = abs(current["low"] - eql) / eql
            if current["low"] >= eql and proximity <= 0.002:
                return [{
                    "symbol": "_",
                    "timeframe": "_",
                    "pattern": "EQL",
                    "type": "EQL",
                    "detail": f"EQL: {ts_utc(current['time'])} | {fmt_price(eql)} | Equal Lows - SSL below ({len(matches)} touches)",
                    "direction": "Bullish",
                    "score": None,
                    "level": eql,
                    "time": current["time"],
                    "alert_kind": "primitive",
                }]
    return []


def detect_volume(candles: list[dict]) -> list[dict]:
    if len(candles) < 22:
        return []
    last = candles[-2]
    avg_vol = sum(c["volume"] for c in candles[-22:-2]) / 20
    if avg_vol == 0:
        return []
    ratio = last["volume"] / avg_vol
    if ratio < 2.0:
        return []
    pct = (ratio - 1) * 100
    usd_vol = last["volume"] * last["close"]
    usd_str = f"${usd_vol/1_000_000:.1f}M" if usd_vol >= 1_000_000 else f"${usd_vol/1_000:.0f}K"
    tier = "Extreme" if ratio >= 5.0 else "Elevated" if ratio >= 3.0 else "Notable"
    direction = "Bullish" if last["close"] >= last["open"] else "Bearish"
    return [{
        "symbol": "_",
        "timeframe": "_",
        "pattern": "Volume",
        "type": "Volume",
        "detail": f"VOLUME: {ts_utc(last['time'])} | {usd_str} | +{pct:.0f}% avg | {tier} {direction}",
        "direction": direction,
        "score": None,
        "level": last["volume"],
        "time": last["time"],
        "alert_kind": "primitive",
    }]


def detect_volume_profile(candles: list[dict]) -> list[dict]:
    if len(candles) < 35:
        return []
    closed = candles[:-1]
    window = closed[-48:]
    prices = [c["close"] for c in window]
    low = min(prices)
    high = max(prices)
    if high <= low:
        return []
    bins = 24
    step = (high - low) / bins
    hist = [0.0] * bins
    for candle in window:
        idx = min(int((candle["close"] - low) / step), bins - 1)
        hist[idx] += candle["volume"]
    poc_idx = max(range(bins), key=lambda item: hist[item])
    poc = low + (poc_idx + 0.5) * step
    current = closed[-1]
    if abs(current["close"] - poc) / poc > 0.003:
        return []
    direction = "Bullish" if current["close"] >= current["open"] else "Bearish"
    return [{
        "symbol": "_",
        "timeframe": "_",
        "pattern": "VP",
        "type": "VP",
        "detail": f"VP: {ts_utc(current['time'])} | POC {fmt_price(poc)} | Price at high-volume node",
        "direction": direction,
        "score": None,
        "level": poc,
        "time": current["time"],
        "alert_kind": "primitive",
    }]


def detect_key_levels(candles: list[dict]) -> list[dict]:
    if len(candles) < 35:
        return []
    closed = candles[:-1]
    swing_highs, swing_lows = collect_swings(closed[-60:], "_", "_")
    levels = [item.level for item in swing_highs] + [item.level for item in swing_lows]
    clusters = cluster_levels(levels, tolerance=0.0025)
    current = closed[-1]
    nearby = []
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        level = sum(cluster) / len(cluster)
        if abs(current["close"] - level) / level <= 0.0035:
            direction = "Bullish" if current["close"] >= level else "Bearish"
            nearby.append((len(cluster), level, direction))
    if not nearby:
        return []
    touches, level, direction = max(nearby, key=lambda item: (item[0], -abs(current["close"] - item[1])))
    bias = "support" if direction == "Bullish" else "resistance"
    return [{
        "symbol": "_",
        "timeframe": "_",
        "pattern": "KL",
        "type": "KL",
        "detail": f"KEY LEVEL: {ts_utc(current['time'])} | {fmt_price(level)} | {touches} touches ({bias})",
        "direction": direction,
        "score": None,
        "level": level,
        "time": current["time"],
        "alert_kind": "primitive",
    }]


def detect_pd_zones(candles: list[dict]) -> list[dict]:
    if len(candles) < 30:
        return []
    scan = candles[-51:-1]
    prev = candles[-2]
    current = candles[-1]
    swing_highs, swing_lows = collect_swings(scan, "_", "_")
    if not swing_highs or not swing_lows:
        return []
    last_high = swing_highs[-1]
    last_low = swing_lows[-1]
    hi = last_high.level
    lo = last_low.level
    eq = (hi + lo) / 2
    results = []
    if last_low.index > last_high.index:
        ote_lo = lo + (hi - lo) * 0.618
        ote_hi = lo + (hi - lo) * 0.786
        if ote_lo <= current["high"] <= ote_hi and not (ote_lo <= prev["high"] <= ote_hi):
            results.append({
                "symbol": "_",
                "timeframe": "_",
                "pattern": "PD",
                "type": "PD",
                "detail": f"OTE ZONE: {ts_utc(current['time'])} | {fmt_price(ote_lo)} - {fmt_price(ote_hi)} | Bullish OTE",
                "direction": "Discount",
                "score": None,
                "level": eq,
                "time": current["time"],
                "alert_kind": "primitive",
            })
    elif last_high.index > last_low.index:
        ote_hi = hi - (hi - lo) * 0.618
        ote_lo = hi - (hi - lo) * 0.786
        if ote_lo <= current["low"] <= ote_hi and not (ote_lo <= prev["low"] <= ote_hi):
            results.append({
                "symbol": "_",
                "timeframe": "_",
                "pattern": "PD",
                "type": "PD",
                "detail": f"OTE ZONE: {ts_utc(current['time'])} | {fmt_price(ote_lo)} - {fmt_price(ote_hi)} | Bearish OTE",
                "direction": "Premium",
                "score": None,
                "level": eq,
                "time": current["time"],
                "alert_kind": "primitive",
            })
    if results:
        return results
    if prev["close"] <= eq < current["close"]:
        return [{
            "symbol": "_",
            "timeframe": "_",
            "pattern": "PD",
            "type": "PD",
            "detail": f"PREMIUM: {ts_utc(current['time'])} | EQ {fmt_price(eq)} | Above equilibrium",
            "direction": "Premium",
            "score": None,
            "level": eq,
            "time": current["time"],
            "alert_kind": "primitive",
        }]
    if prev["close"] >= eq > current["close"]:
        return [{
            "symbol": "_",
            "timeframe": "_",
            "pattern": "PD",
            "type": "PD",
            "detail": f"DISCOUNT: {ts_utc(current['time'])} | EQ {fmt_price(eq)} | Below equilibrium",
            "direction": "Discount",
            "score": None,
            "level": eq,
            "time": current["time"],
            "alert_kind": "primitive",
        }]
    return []


def detect_smt(candles_a: list[dict], candles_b: list[dict], sym_a: str, sym_b: str) -> list[dict]:
    if len(candles_a) < 10 or len(candles_b) < 10:
        return []
    cb_by_time = {c["time"]: c for c in candles_b[-41:-1]}
    aligned_a = []
    aligned_b = []
    for candle in candles_a[-41:-1]:
        other = cb_by_time.get(candle["time"])
        if other:
            aligned_a.append(candle)
            aligned_b.append(other)
    if len(aligned_a) < 10:
        return []
    swing_highs, swing_lows = collect_swings(aligned_a, sym_a, "_", left=1, right=1)
    results = []
    if len(swing_highs) >= 2:
        first, second = swing_highs[-2], swing_highs[-1]
        if second.level > first.level:
            b1 = aligned_b[first.index]["high"]
            b2 = aligned_b[second.index]["high"]
            if b2 < b1 and len(aligned_a) - 1 - second.index <= 8:
                results.append({
                    "symbol": sym_a,
                    "timeframe": "_",
                    "pattern": "SMT",
                    "type": "SMT",
                    "detail": f"SMT Bearish: {sym_a} HH {fmt_price(second.level)} / {sym_b} LH {fmt_price(b2)} - divergence",
                    "direction": "Bearish",
                    "score": None,
                    "level": second.level,
                    "time": second.timestamp,
                    "alert_kind": "primitive",
                })
    if len(swing_lows) >= 2:
        first, second = swing_lows[-2], swing_lows[-1]
        if second.level < first.level:
            b1 = aligned_b[first.index]["low"]
            b2 = aligned_b[second.index]["low"]
            if b2 > b1 and len(aligned_a) - 1 - second.index <= 8:
                results.append({
                    "symbol": sym_a,
                    "timeframe": "_",
                    "pattern": "SMT",
                    "type": "SMT",
                    "detail": f"SMT Bullish: {sym_a} LL {fmt_price(second.level)} / {sym_b} HL {fmt_price(b2)} - divergence",
                    "direction": "Bullish",
                    "score": None,
                    "level": second.level,
                    "time": second.timestamp,
                    "alert_kind": "primitive",
                })
    return results


def check_confluence(symbol: str, results_by_tf: dict) -> list[str]:
    tf_signals: dict[tuple[str, str], list[str]] = {}
    for tf, patterns in results_by_tf.items():
        for pattern in patterns:
            key = (pattern["pattern"], pattern.get("direction", ""))
            tf_signals.setdefault(key, []).append(tf)
    messages = []
    for (pattern, direction), timeframes in tf_signals.items():
        if len(timeframes) >= 2:
            tfs = " + ".join(sorted(timeframes))
            messages.append(f"{symbol} - CONFLUENCE: {pattern} {direction} on {tfs}")
    return messages


_PATTERN_WEIGHTS = {
    "CHoCH": 1.0,
    "BOS": 0.9,
    "SMT": 0.9,
    "IFVG": 0.8,
    "Breaker": 0.8,
    "OB": 0.7,
    "EQH": 0.7,
    "EQL": 0.7,
    "Liquidity": 0.8,
    "KL": 0.6,
    "FVG": 0.6,
    "Sweeps": 0.6,
    "Volume": 0.4,
    "VP": 0.4,
    "PD": 0.4,
    "Swings": 0.3,
}
_TF_WEIGHT = {"1m": 0.4, "5m": 0.5, "15m": 0.6, "30m": 0.7, "1h": 0.8, "4h": 0.9, "1d": 1.0}


def score_signal(symbol: str, timeframe: str, patterns: dict, cache: dict[tuple[str, str], PrimitiveSnapshot]) -> int:
    if not patterns:
        return 1
    raw = sum(_PATTERN_WEIGHTS.get(name, 0.3) for name in patterns)
    tf_weight = _TF_WEIGHT.get(timeframe, 0.6)
    snapshot = cache.get((symbol, timeframe))
    dir_mult = _directional_agreement(snapshot)
    confidence = raw * tf_weight * dir_mult
    if confidence < 0.4:
        return 1
    if confidence < 0.8:
        return 2
    if confidence < 1.3:
        return 3
    if confidence < 2.0:
        return 4
    return 5


def _directional_agreement(snapshot: PrimitiveSnapshot | None) -> float:
    if snapshot is None:
        return 0.75
    directions = [item.direction for item in snapshot.structure_breaks]
    directions += [item.direction for item in snapshot.sweeps]
    directions += [item.direction for item in snapshot.raids]
    if not directions:
        return 0.75
    bullish = sum(1 for item in directions if item == "bullish")
    bearish = sum(1 for item in directions if item == "bearish")
    total = bullish + bearish
    if total == 0:
        return 0.75
    return max(0.5, max(bullish, bearish) / total)


def score_to_stars(score: int) -> str:
    return f"{'*' * score}{'.' * (5 - score)}"


def _legacy_snapshot(candles: list[dict]) -> PrimitiveSnapshot:
    return _snapshot_for("_", "_", candles)


def _legacy_swing_dict(swing: SwingPoint) -> dict:
    return {
        "index": swing.index,
        "time": swing.timestamp,
        "level": swing.level,
        "candle": {"time": swing.timestamp},
    }


def _collect_swings(candles: list[dict], left: int = 2, right: int = 2) -> tuple[list[dict], list[dict]]:
    highs, lows = collect_swings(candles, "_", "_", left=left, right=right)
    return ([_legacy_swing_dict(item) for item in highs], [_legacy_swing_dict(item) for item in lows])


def detect_fvg(candles: list[dict]) -> list[dict]:
    return [_fvg_to_alert(item, "FVG") for item in active_fvgs(candles, "_", "_")[:1]]


def detect_ifvg(candles: list[dict]) -> list[dict]:
    return [_ifvg_to_alert(item) for item in primitive_detect_ifvg(candles, "_", "_")[:1]]


def detect_ob(candles: list[dict]) -> list[dict]:
    return [_order_block_to_alert(item) for item in detect_order_blocks(candles, "_", "_")[:1]]


def detect_breaker(candles: list[dict]) -> list[dict]:
    return [_breaker_to_alert(item) for item in detect_breaker_blocks(candles, "_", "_")[:1]]


def detect_bos(candles: list[dict]) -> list[dict]:
    return [_structure_to_alert(item) | {"pattern": "BOS"} for item in detect_structure_breaks(candles, "_", "_") if item.break_type == "BOS"]


def detect_choch(candles: list[dict]) -> list[dict]:
    return [_structure_to_alert(item) | {"pattern": "CHoCH"} for item in detect_structure_breaks(candles, "_", "_") if item.break_type == "CHOCH"]


def detect_swings(candles: list[dict]) -> list[dict]:
    return [_swing_to_alert(item) for item in primitive_detect_swings(candles, "_", "_")]


def detect_sweeps(candles: list[dict]) -> list[dict]:
    return [_sweep_to_alert(item, "Sweeps") for item in primitive_detect_sweeps(candles, "_", "_")]


def detect_liquidity_raids(candles: list[dict]) -> list[dict]:
    return [_sweep_to_alert(item, "Liquidity") for item in primitive_detect_liquidity_raids(candles, "_", "_")]
