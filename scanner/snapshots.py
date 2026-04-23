from __future__ import annotations

from market_primitives import (
    detect_breaker_blocks,
    detect_eqh,
    detect_eql,
    detect_fvg,
    detect_ifvg,
    detect_key_levels,
    detect_liquidity_raids,
    detect_order_blocks,
    detect_pd_zones,
    detect_structure_breaks,
    detect_sweeps,
    detect_swings,
    detect_volume,
    detect_volume_profile,
)
from strategies.types import PrimitiveSnapshot


def build_primitive_snapshot(symbol: str, timeframe: str, candles: list[dict]) -> PrimitiveSnapshot:
    return PrimitiveSnapshot(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        swings=detect_swings(candles, symbol, timeframe),
        sweeps=detect_sweeps(candles, symbol, timeframe),
        raids=detect_liquidity_raids(candles, symbol, timeframe),
        structure_breaks=detect_structure_breaks(candles, symbol, timeframe),
        fvgs=detect_fvg(candles, symbol, timeframe),
        ifvgs=detect_ifvg(candles, symbol, timeframe),
        order_blocks=detect_order_blocks(candles, symbol, timeframe),
        breaker_blocks=detect_breaker_blocks(candles, symbol, timeframe),
        equal_highs=detect_eqh(candles, symbol, timeframe),
        equal_lows=detect_eql(candles, symbol, timeframe),
        key_levels=detect_key_levels(candles, symbol, timeframe),
        volume_signals=detect_volume(candles, symbol, timeframe) + detect_volume_profile(candles, symbol, timeframe),
        pd_zones=detect_pd_zones(candles, symbol, timeframe),
    )


__all__ = ["build_primitive_snapshot"]
