from __future__ import annotations

from backtesting import Candle
from backtesting.accumulator import ReplaySnapshotCache
from scanner.snapshots import build_primitive_snapshot
from strategies import StrategyContext
from strategies.htf_context import build_htf_context
from strategies.setup_utils import current_price
from timeframes import MODEL_3_LTF_MAP, execution_htf_for

CandleStore = dict[tuple[str, str], list[Candle]]


def slice_candles_until(candles: list[Candle], timestamp: int) -> list[Candle]:
    return [candle for candle in candles if int(candle["time"]) <= timestamp]


def build_strategy_context_for_replay(
    *,
    symbol: str,
    timeframe: str,
    primary_visible: list[Candle],
    current_timestamp: int,
    candle_store: CandleStore,
    higher_timeframe: str | None = None,
    lower_timeframe: str | None = None,
    htf_mode: str = "strict",
) -> StrategyContext:
    primary = build_primitive_snapshot(symbol, timeframe, primary_visible)

    htf = higher_timeframe if higher_timeframe is not None else execution_htf_for(timeframe)
    ltf = lower_timeframe if lower_timeframe is not None else MODEL_3_LTF_MAP.get(timeframe)

    higher = None
    htf_context = None
    if htf:
        # Lookahead guard: HTF context is sliced to the current primary bar timestamp.
        # Future HTF candles are never passed into primitive detectors or strategies.
        visible = slice_candles_until(candle_store.get((symbol, htf), []), current_timestamp)
        if visible:
            higher = build_primitive_snapshot(symbol, htf, visible)
            htf_context = build_htf_context(higher, current_price(primary))

    lower = None
    if ltf:
        # Lookahead guard: LTF context is also timestamp-sliced before snapshot creation.
        visible = slice_candles_until(candle_store.get((symbol, ltf), []), current_timestamp)
        if visible:
            lower = build_primitive_snapshot(symbol, ltf, visible)

    return StrategyContext(
        primary=primary,
        higher_timeframe=higher,
        lower_timeframe=lower,
        htf_context=htf_context,
        htf_timeframe=htf,
        execution_timeframe=timeframe,
        htf_mode=htf_mode,
    )


def build_accumulated_strategy_context_for_replay(
    *,
    symbol: str,
    timeframe: str,
    current_timestamp: int,
    snapshot_cache: ReplaySnapshotCache,
    higher_timeframe: str | None = None,
    lower_timeframe: str | None = None,
    htf_mode: str = "strict",
) -> StrategyContext | None:
    primary = snapshot_cache.get_snapshot(symbol, timeframe, current_timestamp)
    if primary is None:
        return None

    htf = higher_timeframe if higher_timeframe is not None else execution_htf_for(timeframe)
    ltf = lower_timeframe if lower_timeframe is not None else MODEL_3_LTF_MAP.get(timeframe)

    higher = snapshot_cache.get_snapshot(symbol, htf, current_timestamp) if htf else None
    lower = snapshot_cache.get_snapshot(symbol, ltf, current_timestamp) if ltf else None
    return StrategyContext(
        primary=primary,
        higher_timeframe=higher,
        lower_timeframe=lower,
        htf_context=build_htf_context(higher, current_price(primary)) if higher is not None else None,
        htf_timeframe=htf,
        execution_timeframe=timeframe,
        htf_mode=htf_mode,
    )


__all__ = [
    "CandleStore",
    "build_accumulated_strategy_context_for_replay",
    "build_strategy_context_for_replay",
    "slice_candles_until",
]
