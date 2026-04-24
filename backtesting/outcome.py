from __future__ import annotations

from backtesting import BacktestEvent, BacktestOutcome, Candle


def evaluate_forward_outcome(event: BacktestEvent, future_candles: list[Candle]) -> BacktestOutcome:
    # Future candles are used only here, after a setup event has already been fixed
    # by the bar-by-bar replay loop. They must never be fed back into context building.
    future_high = max((float(candle["high"]) for candle in future_candles), default=None)
    future_low = min((float(candle["low"]) for candle in future_candles), default=None)

    entry = event.entry_price
    risk = event.risk
    if entry is None or future_high is None or future_low is None:
        return BacktestOutcome(
            event_id=event.event_id,
            forward_bars=len(future_candles),
            mfe=None,
            mae=None,
            mfe_r=None,
            mae_r=None,
            hit_0_5r=False,
            hit_1r=False,
            hit_2r=False,
            invalidated=False,
            bars_to_0_5r=None,
            bars_to_1r=None,
            bars_to_2r=None,
            bars_to_invalidation=None,
            future_high=future_high,
            future_low=future_low,
            hit_1r_before_invalidation=False,
            hit_2r_before_invalidation=False,
        )

    if event.direction == "long":
        mfe = max(0.0, future_high - entry)
        mae = max(0.0, entry - future_low)
    else:
        mfe = max(0.0, entry - future_low)
        mae = max(0.0, future_high - entry)

    bars_to_invalidation = _bars_to_invalidation(event, future_candles)
    mfe_r = mfe / risk if risk and risk > 0 else None
    mae_r = mae / risk if risk and risk > 0 else None
    bars_to_0_5r = _bars_to_r(event, future_candles, 0.5) if risk and risk > 0 else None
    bars_to_1r = _bars_to_r(event, future_candles, 1.0) if risk and risk > 0 else None
    bars_to_2r = _bars_to_r(event, future_candles, 2.0) if risk and risk > 0 else None

    return BacktestOutcome(
        event_id=event.event_id,
        forward_bars=len(future_candles),
        mfe=mfe,
        mae=mae,
        mfe_r=mfe_r,
        mae_r=mae_r,
        hit_0_5r=bool(mfe_r is not None and mfe_r >= 0.5),
        hit_1r=bool(mfe_r is not None and mfe_r >= 1.0),
        hit_2r=bool(mfe_r is not None and mfe_r >= 2.0),
        invalidated=bars_to_invalidation is not None,
        bars_to_0_5r=bars_to_0_5r,
        bars_to_1r=bars_to_1r,
        bars_to_2r=bars_to_2r,
        bars_to_invalidation=bars_to_invalidation,
        future_high=future_high,
        future_low=future_low,
        hit_1r_before_invalidation=_before_or_without_invalidation(bars_to_1r, bars_to_invalidation),
        hit_2r_before_invalidation=_before_or_without_invalidation(bars_to_2r, bars_to_invalidation),
    )


def _bars_to_r(event: BacktestEvent, future_candles: list[Candle], multiple: float) -> int | None:
    if event.entry_price is None or event.risk is None or event.risk <= 0:
        return None
    target_move = event.risk * multiple
    for index, candle in enumerate(future_candles, start=1):
        if event.direction == "long" and float(candle["high"]) - event.entry_price >= target_move:
            return index
        if event.direction == "short" and event.entry_price - float(candle["low"]) >= target_move:
            return index
    return None


def _bars_to_invalidation(event: BacktestEvent, future_candles: list[Candle]) -> int | None:
    if event.invalidation is None:
        return None
    for index, candle in enumerate(future_candles, start=1):
        if event.direction == "long" and float(candle["low"]) <= event.invalidation:
            return index
        if event.direction == "short" and float(candle["high"]) >= event.invalidation:
            return index
    return None


def _before_or_without_invalidation(bars_to_hit: int | None, bars_to_invalidation: int | None) -> bool:
    if bars_to_hit is None:
        return False
    if bars_to_invalidation is None:
        return True
    return bars_to_hit <= bars_to_invalidation


__all__ = ["evaluate_forward_outcome"]
