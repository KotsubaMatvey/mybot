from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from backtesting import Candle
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

DEFAULT_MAX_PRIMITIVES_PER_FIELD = 1500
DEFAULT_DETECTOR_WINDOW = 200
DEFAULT_SNAPSHOT_CANDLE_WINDOW = 1500


@dataclass(slots=True)
class _SnapshotState:
    next_index: int = 0
    swings: dict[tuple[Any, ...], Any] | None = None
    sweeps: dict[tuple[Any, ...], Any] | None = None
    raids: dict[tuple[Any, ...], Any] | None = None
    structure_breaks: dict[tuple[Any, ...], Any] | None = None
    fvgs: dict[tuple[Any, ...], Any] | None = None
    ifvgs: dict[tuple[Any, ...], Any] | None = None
    order_blocks: dict[tuple[Any, ...], Any] | None = None
    breaker_blocks: dict[tuple[Any, ...], Any] | None = None
    equal_highs: dict[tuple[Any, ...], Any] | None = None
    equal_lows: dict[tuple[Any, ...], Any] | None = None
    key_levels: dict[tuple[Any, ...], Any] | None = None
    volume_signals: dict[tuple[Any, ...], Any] | None = None
    pd_zones: dict[tuple[Any, ...], Any] | None = None
    smt_divergences: dict[tuple[Any, ...], Any] | None = None

    def __post_init__(self) -> None:
        for name in _PRIMITIVE_LIST_FIELDS:
            if getattr(self, name) is None:
                setattr(self, name, {})


_PRIMITIVE_LIST_FIELDS = (
    "swings",
    "sweeps",
    "raids",
    "structure_breaks",
    "fvgs",
    "ifvgs",
    "order_blocks",
    "breaker_blocks",
    "equal_highs",
    "equal_lows",
    "key_levels",
    "volume_signals",
    "pd_zones",
    "smt_divergences",
)


class PrimitiveSnapshotAccumulator:
    def __init__(
        self,
        symbol: str,
        timeframe: str,
        candles: list[Candle],
        *,
        max_primitives_per_field: int = DEFAULT_MAX_PRIMITIVES_PER_FIELD,
        detector_window: int = DEFAULT_DETECTOR_WINDOW,
        snapshot_candle_window: int = DEFAULT_SNAPSHOT_CANDLE_WINDOW,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = candles
        self.max_primitives_per_field = max_primitives_per_field
        self.detector_window = detector_window
        self.snapshot_candle_window = snapshot_candle_window
        self.state = _SnapshotState()

    def snapshot_until(self, timestamp: int) -> PrimitiveSnapshot:
        while self.state.next_index < len(self.candles):
            candle = self.candles[self.state.next_index]
            if int(candle["time"]) > timestamp:
                break
            visible_start = max(0, self.state.next_index + 1 - self.detector_window)
            visible = self.candles[visible_start : self.state.next_index + 1]
            # Lookahead guard: this calls the same live primitive detectors, but only
            # with recent candles visible at the current replay bar. The live detectors
            # use bounded lookbacks, and detected primitives are accumulated after they
            # become visible; future candles are not used here.
            latest = _build_entry_model_snapshot(self.symbol, self.timeframe, visible)
            self._merge(latest)
            self.state.next_index += 1

        snapshot_start = max(0, self.state.next_index - self.snapshot_candle_window)
        visible_now = self.candles[snapshot_start : self.state.next_index]
        return PrimitiveSnapshot(
            symbol=self.symbol,
            timeframe=self.timeframe,
            candles=visible_now,
            swings=self._values("swings"),
            sweeps=self._values("sweeps"),
            raids=self._values("raids"),
            structure_breaks=self._values("structure_breaks"),
            fvgs=self._values("fvgs"),
            ifvgs=self._values("ifvgs"),
            order_blocks=self._values("order_blocks"),
            breaker_blocks=self._values("breaker_blocks"),
            equal_highs=self._values("equal_highs"),
            equal_lows=self._values("equal_lows"),
            key_levels=self._values("key_levels"),
            volume_signals=self._values("volume_signals"),
            pd_zones=self._values("pd_zones"),
            smt_divergences=self._values("smt_divergences"),
        )

    def _merge(self, snapshot: PrimitiveSnapshot) -> None:
        for field_name in _PRIMITIVE_LIST_FIELDS:
            bucket = getattr(self.state, field_name)
            for item in getattr(snapshot, field_name):
                bucket[_primitive_key(field_name, item)] = item
            self._prune(bucket)

    def _prune(self, bucket: dict[tuple[Any, ...], Any]) -> None:
        if self.max_primitives_per_field <= 0 or len(bucket) <= self.max_primitives_per_field:
            return
        ordered_keys = sorted(bucket, key=lambda key: _primitive_sort_key(bucket[key]))
        remove_count = len(ordered_keys) - self.max_primitives_per_field
        for key in ordered_keys[:remove_count]:
            del bucket[key]

    def _values(self, field_name: str) -> list[Any]:
        bucket = getattr(self.state, field_name)
        return sorted(bucket.values(), key=_primitive_sort_key)


class ReplaySnapshotCache:
    def __init__(
        self,
        candle_store: dict[tuple[str, str], list[Candle]],
        *,
        max_primitives_per_field: int = DEFAULT_MAX_PRIMITIVES_PER_FIELD,
        detector_window: int = DEFAULT_DETECTOR_WINDOW,
        snapshot_candle_window: int = DEFAULT_SNAPSHOT_CANDLE_WINDOW,
    ) -> None:
        self.candle_store = candle_store
        self.max_primitives_per_field = max_primitives_per_field
        self.detector_window = detector_window
        self.snapshot_candle_window = snapshot_candle_window
        self.accumulators: dict[tuple[str, str], PrimitiveSnapshotAccumulator] = {}

    def get_snapshot(self, symbol: str, timeframe: str, timestamp: int) -> PrimitiveSnapshot | None:
        candles = self.candle_store.get((symbol, timeframe), [])
        if not candles:
            return None
        key = (symbol, timeframe)
        accumulator = self.accumulators.get(key)
        if accumulator is None:
            accumulator = PrimitiveSnapshotAccumulator(
                symbol,
                timeframe,
                candles,
                max_primitives_per_field=self.max_primitives_per_field,
                detector_window=self.detector_window,
                snapshot_candle_window=self.snapshot_candle_window,
            )
            self.accumulators[key] = accumulator
        return accumulator.snapshot_until(timestamp)


def _primitive_key(field_name: str, item: Any) -> tuple[Any, ...]:
    if field_name == "swings":
        return (field_name, item.direction, item.timestamp, round(float(item.level), 8))
    if field_name in {"sweeps", "raids"}:
        return (
            field_name,
            item.direction,
            item.timestamp,
            round(float(item.liquidity_level), 8),
            round(float(item.wick_extreme), 8),
        )
    if field_name == "structure_breaks":
        return (
            field_name,
            item.break_type,
            item.direction,
            item.timestamp,
            round(float(item.broken_level), 8),
        )
    if field_name == "fvgs":
        return (field_name, item.direction, item.created_at, round(float(item.gap_low), 8), round(float(item.gap_high), 8))
    if field_name == "ifvgs":
        return (
            field_name,
            item.direction,
            item.source_direction,
            item.invalidated_at,
            round(float(item.zone_low), 8),
            round(float(item.zone_high), 8),
        )
    if field_name == "order_blocks":
        return (
            field_name,
            item.direction,
            item.origin_time,
            round(float(item.zone_low), 8),
            round(float(item.zone_high), 8),
        )
    if field_name == "breaker_blocks":
        return (
            field_name,
            item.direction,
            item.origin_time,
            item.trigger_time,
            round(float(item.zone_low), 8),
            round(float(item.zone_high), 8),
        )
    return (field_name, _object_identity(item))


def _object_identity(item: Any) -> tuple[Any, ...]:
    if is_dataclass(item):
        values = []
        for field in fields(item):
            if field.name == "metadata":
                continue
            value = getattr(item, field.name)
            if isinstance(value, float):
                value = round(value, 8)
            values.append((field.name, value))
        return tuple(values)
    return (repr(item),)


def _primitive_sort_key(item: Any) -> tuple[int, str]:
    timestamp = (
        getattr(item, "timestamp", None)
        or getattr(item, "created_at", None)
        or getattr(item, "invalidated_at", None)
        or getattr(item, "trigger_time", None)
        or 0
    )
    return int(timestamp), type(item).__name__


def _build_entry_model_snapshot(symbol: str, timeframe: str, candles: list[Candle]) -> PrimitiveSnapshot:
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


__all__ = [
    "DEFAULT_DETECTOR_WINDOW",
    "DEFAULT_MAX_PRIMITIVES_PER_FIELD",
    "DEFAULT_SNAPSHOT_CANDLE_WINDOW",
    "PrimitiveSnapshotAccumulator",
    "ReplaySnapshotCache",
]
