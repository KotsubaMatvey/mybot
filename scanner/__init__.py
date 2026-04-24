from __future__ import annotations

from market_primitives import active_fvgs, collect_swings
from market_primitives import detect_breaker_blocks as primitive_detect_breaker_blocks
from market_primitives import detect_eqh as primitive_detect_eqh
from market_primitives import detect_eql as primitive_detect_eql
from market_primitives import detect_ifvg as primitive_detect_ifvg
from market_primitives import detect_key_levels as primitive_detect_key_levels
from market_primitives import detect_liquidity_raids as primitive_detect_liquidity_raids
from market_primitives import detect_order_blocks as primitive_detect_order_blocks
from market_primitives import detect_pd_zones as primitive_detect_pd_zones
from market_primitives import detect_structure_breaks as primitive_detect_structure_breaks
from market_primitives import detect_sweeps as primitive_detect_sweeps
from market_primitives import detect_volume as primitive_detect_volume
from market_primitives import detect_volume_profile as primitive_detect_volume_profile
from presentation.alert_builders import (
    from_breaker_block,
    from_equal_level,
    from_fvg,
    from_ifvg,
    from_key_level,
    from_order_block,
    from_pd_zone,
    from_structure_break,
    from_sweep,
    from_volume_signal,
)
from scanner.cache import get_active_zones, get_cached_candles, get_cached_patterns
from scanner.engine import (
    ALL_PATTERNS,
    EXECUTION_HTF_MAP,
    MODEL_3_HTF_MAP,
    MODEL_3_LTF_MAP,
    PRIMITIVE_PATTERNS,
    STRATEGY_PATTERNS,
    run_scanner,
)


def _legacy_swing_dict(swing) -> dict:
    return {
        "index": swing.index,
        "time": swing.timestamp,
        "level": swing.level,
        "candle": {"time": swing.timestamp},
    }


def _legacy_alert(alert, pattern_override: str | None = None) -> dict:
    payload = {
        "symbol": alert.symbol,
        "timeframe": alert.timeframe,
        "pattern": pattern_override or alert.pattern,
        "type": pattern_override or alert.pattern,
        "detail": alert.detail,
        "direction": alert.direction,
        "score": alert.score,
        "level": alert.level,
        "time": alert.timestamp,
        "gap_low": alert.gap_low,
        "gap_high": alert.gap_high,
        "ob_low": alert.ob_low,
        "ob_high": alert.ob_high,
        "entry_low": alert.entry_low,
        "entry_high": alert.entry_high,
        "invalidation": alert.invalidation,
        "sweep_level": alert.sweep_level,
        "structure_level": alert.structure_level,
        "context_timeframe": alert.context_timeframe,
        "alert_kind": alert.alert_kind,
    }
    return {key: value for key, value in payload.items() if value is not None}


def _collect_swings(candles: list[dict], left: int = 2, right: int = 2) -> tuple[list[dict], list[dict]]:
    highs, lows = collect_swings(candles, "offline", "offline", left=left, right=right)
    return ([_legacy_swing_dict(item) for item in highs], [_legacy_swing_dict(item) for item in lows])


def detect_bos(candles: list[dict]) -> list[dict]:
    return [
        _legacy_alert(from_structure_break(item), "BOS")
        for item in primitive_detect_structure_breaks(candles, "offline", "offline")
        if item.break_type == "BOS"
    ]


def detect_choch(candles: list[dict]) -> list[dict]:
    return [
        _legacy_alert(from_structure_break(item), "CHoCH")
        for item in primitive_detect_structure_breaks(candles, "offline", "offline")
        if item.break_type == "CHOCH"
    ]


def detect_sweeps(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_sweep(item, "Sweeps")) for item in primitive_detect_sweeps(candles, "offline", "offline")]


def detect_liquidity_raids(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_sweep(item, "Liquidity")) for item in primitive_detect_liquidity_raids(candles, "offline", "offline")]


def detect_key_levels(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_key_level(item)) for item in primitive_detect_key_levels(candles, "offline", "offline")]


def detect_volume_profile(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_volume_signal(item)) for item in primitive_detect_volume_profile(candles, "offline", "offline")]


def detect_volume(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_volume_signal(item)) for item in primitive_detect_volume(candles, "offline", "offline")]


def detect_eqh(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_equal_level(item, "EQH")) for item in primitive_detect_eqh(candles, "offline", "offline")]


def detect_eql(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_equal_level(item, "EQL")) for item in primitive_detect_eql(candles, "offline", "offline")]


def detect_pd_zones(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_pd_zone(item)) for item in primitive_detect_pd_zones(candles, "offline", "offline")]


def detect_fvg(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_fvg(item)) for item in active_fvgs(candles, "offline", "offline")[:1]]


def detect_ifvg(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_ifvg(item)) for item in primitive_detect_ifvg(candles, "offline", "offline")[:1]]


def detect_ob(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_order_block(item)) for item in primitive_detect_order_blocks(candles, "offline", "offline")[:1]]


def detect_breaker(candles: list[dict]) -> list[dict]:
    return [_legacy_alert(from_breaker_block(item)) for item in primitive_detect_breaker_blocks(candles, "offline", "offline")[:1]]


__all__ = [
    "ALL_PATTERNS",
    "EXECUTION_HTF_MAP",
    "MODEL_3_HTF_MAP",
    "MODEL_3_LTF_MAP",
    "PRIMITIVE_PATTERNS",
    "STRATEGY_PATTERNS",
    "_collect_swings",
    "detect_bos",
    "detect_breaker",
    "detect_choch",
    "detect_eqh",
    "detect_eql",
    "detect_fvg",
    "detect_ifvg",
    "detect_key_levels",
    "detect_liquidity_raids",
    "detect_ob",
    "detect_pd_zones",
    "detect_sweeps",
    "detect_volume",
    "detect_volume_profile",
    "get_active_zones",
    "get_cached_candles",
    "get_cached_patterns",
    "run_scanner",
]
