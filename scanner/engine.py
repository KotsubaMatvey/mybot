from __future__ import annotations

import asyncio
import logging
from collections import defaultdict

import aiohttp

from config import CANDLE_LIMIT, SYMBOLS, TIMEFRAMES
from market_primitives import detect_smt
from presentation.alert_builders import build_primitive_alerts, from_entry_setup, from_smt_divergence
from presentation.types import AlertPayload
from scanner.cache import (
    get_active_zones,
    get_cached_candles,
    get_cached_patterns,
    replace_active_zones,
    replace_pattern_cache,
    set_cached_candles,
)
from scanner.confluence import build_confluence_messages
from scanner.dedup import should_skip_duplicate
from scanner.scoring import score_primitive_bundle
from scanner.snapshots import build_primitive_snapshot
from strategies import (
    StrategyContext,
    detect_entry_model_1,
    detect_entry_model_2,
    detect_entry_model_3,
)
from strategies.types import PrimitiveSnapshot

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

_sem = asyncio.Semaphore(5)


async def fetch_candles(
    session: aiohttp.ClientSession,
    symbol: str,
    interval: str,
    limit: int = CANDLE_LIMIT,
) -> list[dict]:
    url = f"{BINANCE_BASE}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
            data = await response.json()
        if not isinstance(data, list):
            logger.warning("Unexpected candle payload for %s %s: %s", symbol, interval, data)
            return []
        return [
            {
                "time": int(candle[0]),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            }
            for candle in data
        ]
    except Exception as exc:
        logger.error("fetch_candles %s %s: %s: %s", symbol, interval, type(exc).__name__, exc)
        return []


async def _fetch_with_sem(session: aiohttp.ClientSession, symbol: str, timeframe: str) -> list[dict]:
    async with _sem:
        return await fetch_candles(session, symbol, timeframe)


def _build_strategy_alerts(
    primary: PrimitiveSnapshot,
    higher: PrimitiveSnapshot | None,
    lower: PrimitiveSnapshot | None,
) -> list[AlertPayload]:
    context = StrategyContext(primary=primary, higher_timeframe=higher, lower_timeframe=lower)
    setups = []
    setups.extend(detect_entry_model_1(context))
    setups.extend(detect_entry_model_2(context))
    setups.extend(detect_entry_model_3(context))

    best_by_key: dict[tuple[str, str], AlertPayload] = {}
    for setup in setups:
        payload = from_entry_setup(setup)
        key = (payload.pattern, payload.trade_direction or "")
        existing = best_by_key.get(key)
        if existing is None or (payload.score or 0) > (existing.score or 0):
            best_by_key[key] = payload
    return list(best_by_key.values())


def _score_primitive_alerts(
    symbol: str,
    timeframe: str,
    snapshot: PrimitiveSnapshot,
    alerts: list[AlertPayload],
) -> None:
    bundle = {alert.pattern: alert.detail for alert in alerts if alert.alert_kind == "primitive"}
    if not bundle:
        return
    score = score_primitive_bundle(bundle, timeframe, snapshot)
    for alert in alerts:
        if alert.alert_kind == "primitive":
            alert.score = score


async def run_scanner() -> tuple[list[AlertPayload], list[dict[str, str]], dict[tuple[str, str], list[dict]]]:
    all_alerts: list[AlertPayload] = []
    all_candles: dict[tuple[str, str], list[dict]] = {}
    snapshots: dict[tuple[str, str], PrimitiveSnapshot] = {}
    alerts_by_symbol: dict[str, dict[str, list[AlertPayload]]] = {symbol: {} for symbol in SYMBOLS}

    fetch_timeframes = sorted(set(TIMEFRAMES) | {tf for tf in MODEL_3_LTF_MAP.values() if tf})

    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        combos = [(symbol, timeframe) for symbol in SYMBOLS for timeframe in fetch_timeframes]
        tasks = [_fetch_with_sem(session, symbol, timeframe) for symbol, timeframe in combos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for (symbol, timeframe), candles in zip(combos, results):
        if isinstance(candles, Exception) or not candles:
            continue
        all_candles[(symbol, timeframe)] = candles
        set_cached_candles(symbol, timeframe, candles)

    for (symbol, timeframe), candles in all_candles.items():
        snapshots[(symbol, timeframe)] = build_primitive_snapshot(symbol, timeframe, candles)

    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            primary = snapshots.get((symbol, timeframe))
            if primary is None:
                continue
            higher_tf = MODEL_3_HTF_MAP.get(timeframe)
            lower_tf = MODEL_3_LTF_MAP.get(timeframe)

            primitive_alerts = build_primitive_alerts(
                swings=primary.swings,
                sweeps=primary.sweeps,
                raids=primary.raids,
                structure_breaks=primary.structure_breaks,
                fvgs=primary.fvgs[-2:],
                ifvgs=primary.ifvgs[-2:],
                order_blocks=primary.order_blocks,
                breaker_blocks=primary.breaker_blocks,
                equal_highs=primary.equal_highs,
                equal_lows=primary.equal_lows,
                key_levels=primary.key_levels[:1],
                volume_signals=primary.volume_signals,
                pd_zones=primary.pd_zones,
                smt_divergences=[],
            )
            strategy_alerts = _build_strategy_alerts(
                primary,
                snapshots.get((symbol, higher_tf)) if higher_tf else None,
                snapshots.get((symbol, lower_tf)) if lower_tf else None,
            )
            combined = primitive_alerts + strategy_alerts
            if not combined:
                continue
            _score_primitive_alerts(symbol, timeframe, primary, combined)
            alerts_by_symbol[symbol][timeframe] = combined

    for symbol_a, symbol_b in SMT_PAIRS:
        if symbol_a not in SYMBOLS or symbol_b not in SYMBOLS:
            continue
        for timeframe in TIMEFRAMES:
            if timeframe not in SMT_TIMEFRAMES:
                continue
            candles_a = all_candles.get((symbol_a, timeframe))
            candles_b = all_candles.get((symbol_b, timeframe))
            if not candles_a or not candles_b:
                continue
            divergences = detect_smt(candles_a, candles_b, symbol_a, symbol_b, timeframe)
            for divergence in divergences:
                alert = from_smt_divergence(divergence)
                alerts_by_symbol.setdefault(symbol_a, {}).setdefault(timeframe, []).append(alert)

    active_zones: dict[str, dict[str, list[AlertPayload]]] = {}
    grouped_for_confluence: dict[str, dict[str, list[AlertPayload]]] = defaultdict(dict)

    for symbol, by_timeframe in alerts_by_symbol.items():
        for timeframe, alerts in by_timeframe.items():
            unique_alerts: list[AlertPayload] = []
            for alert in alerts:
                if should_skip_duplicate(alert):
                    continue
                unique_alerts.append(alert)
                all_alerts.append(alert)
            if unique_alerts:
                active_zones.setdefault(symbol, {})[timeframe] = unique_alerts
                grouped_for_confluence[symbol][timeframe] = unique_alerts

    confluences: list[dict[str, str]] = []
    for symbol, by_timeframe in grouped_for_confluence.items():
        for message in build_confluence_messages(symbol, by_timeframe):
            confluences.append({"symbol": symbol, "message": message})

    replace_active_zones(active_zones)
    replace_pattern_cache(all_alerts)
    return all_alerts, confluences, all_candles


__all__ = [
    "ALL_PATTERNS",
    "MODEL_3_HTF_MAP",
    "MODEL_3_LTF_MAP",
    "PRIMITIVE_PATTERNS",
    "STRATEGY_PATTERNS",
    "fetch_candles",
    "get_active_zones",
    "get_cached_candles",
    "get_cached_patterns",
    "run_scanner",
]
