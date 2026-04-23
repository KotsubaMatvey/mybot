from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, TypedDict

Direction = Literal["bullish", "bearish"]
SwingDirection = Literal["high", "low"]
StructureType = Literal["BOS", "CHOCH"]
PDKind = Literal["premium", "discount", "ote_premium", "ote_discount"]
VolumeSignalType = Literal["spike", "profile"]


class Candle(TypedDict):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class SwingPoint:
    symbol: str
    timeframe: str
    direction: SwingDirection
    timestamp: int
    index: int
    level: float
    range_size: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LiquiditySweep:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    liquidity_level: float
    wick_extreme: float
    close_back_inside: float
    source_swing_index: int
    clean: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StructureBreak:
    symbol: str
    timeframe: str
    break_type: StructureType
    direction: Direction
    timestamp: int
    broken_level: float
    close_price: float
    source_swing_index: int
    strength: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FairValueGap:
    symbol: str
    timeframe: str
    direction: Direction
    created_at: int
    gap_low: float
    gap_high: float
    mitigated: bool
    invalidated: bool
    mitigated_at: int | None
    invalidated_at: int | None
    fill_ratio: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class InvertedFVG:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    source_direction: Direction
    zone_low: float
    zone_high: float
    invalidated_at: int
    retest_at: int
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderBlock:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    origin_time: int
    zone_low: float
    zone_high: float
    midpoint: float
    mitigated: bool
    invalidated: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BreakerBlock:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    origin_time: int
    trigger_time: int
    zone_low: float
    zone_high: float
    retested: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EqualLiquidityLevel:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    level: float
    touches: int
    tolerance: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KeyLevel:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    level: float
    touches: int
    bias: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VolumeSignal:
    symbol: str
    timeframe: str
    signal_type: VolumeSignalType
    direction: Direction
    timestamp: int
    level: float
    magnitude: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PDZone:
    symbol: str
    timeframe: str
    kind: PDKind
    timestamp: int
    equilibrium: float
    zone_low: float
    zone_high: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SMTDivergence:
    symbol: str
    timeframe: str
    direction: Direction
    timestamp: int
    primary_level: float
    secondary_symbol: str
    secondary_level: float
    strength: float
    metadata: dict[str, Any] = field(default_factory=dict)


def ts_utc(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%H:%M")


def fmt_price(price: float) -> str:
    if price >= 1000:
        return f"{price:,.1f}"
    if price >= 1:
        return f"{price:.2f}"
    return f"{price:.4f}"


def candle_range(candle: Candle) -> float:
    return abs(candle["high"] - candle["low"])


def average_range(candles: list[Candle]) -> float:
    if not candles:
        return 0.0
    return sum(candle_range(candle) for candle in candles) / len(candles)


def range_threshold(candles: list[Candle], fraction: float = 0.30) -> float:
    return average_range(candles) * fraction


def normalized_zone_width(low: float, high: float) -> float:
    midpoint = (low + high) / 2
    if midpoint <= 0:
        return 0.0
    return abs(high - low) / midpoint


def zone_overlap(a_low: float, a_high: float, b_low: float, b_high: float) -> float:
    overlap = max(0.0, min(a_high, b_high) - max(a_low, b_low))
    denom = max(abs(a_high - a_low), abs(b_high - b_low), 1e-9)
    return overlap / denom


def in_zone(candle: Candle, low: float, high: float) -> bool:
    return candle["low"] <= high and candle["high"] >= low


def touched_zone_after(candles: list[Candle], start_index: int, low: float, high: float) -> int | None:
    for candle in candles[start_index:]:
        if in_zone(candle, low, high):
            return candle["time"]
    return None


def collect_swings(
    candles: list[Candle],
    symbol: str,
    timeframe: str,
    left: int = 2,
    right: int = 2,
    min_range_fraction: float = 0.30,
) -> tuple[list[SwingPoint], list[SwingPoint]]:
    if len(candles) < left + right + 1:
        return [], []

    min_range = range_threshold(candles, min_range_fraction)
    highs: list[SwingPoint] = []
    lows: list[SwingPoint] = []

    for index in range(left, len(candles) - right):
        mid = candles[index]
        if candle_range(mid) < min_range:
            continue

        left_slice = candles[index - left : index]
        right_slice = candles[index + 1 : index + 1 + right]
        neighbors = left_slice + right_slice

        if all(mid["high"] > candle["high"] for candle in neighbors):
            highs.append(
                SwingPoint(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction="high",
                    timestamp=mid["time"],
                    index=index,
                    level=mid["high"],
                    range_size=candle_range(mid),
                )
            )
        if all(mid["low"] < candle["low"] for candle in neighbors):
            lows.append(
                SwingPoint(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction="low",
                    timestamp=mid["time"],
                    index=index,
                    level=mid["low"],
                    range_size=candle_range(mid),
                )
            )
    return highs, lows


def cluster_levels(levels: list[float], tolerance: float = 0.0025) -> list[list[float]]:
    if not levels:
        return []
    ordered = sorted(levels)
    clusters: list[list[float]] = [[ordered[0]]]
    for level in ordered[1:]:
        anchor = sum(clusters[-1]) / len(clusters[-1])
        if anchor > 0 and abs(level - anchor) / anchor <= tolerance:
            clusters[-1].append(level)
        else:
            clusters.append([level])
    return clusters


def nearest_swing_before(swings: list[SwingPoint], index: int) -> SwingPoint | None:
    for swing in reversed(swings):
        if swing.index < index:
            return swing
    return None


__all__ = [
    "BreakerBlock",
    "Candle",
    "Direction",
    "EqualLiquidityLevel",
    "FairValueGap",
    "InvertedFVG",
    "KeyLevel",
    "LiquiditySweep",
    "OrderBlock",
    "PDKind",
    "PDZone",
    "SMTDivergence",
    "StructureBreak",
    "StructureType",
    "SwingDirection",
    "SwingPoint",
    "VolumeSignal",
    "VolumeSignalType",
    "average_range",
    "candle_range",
    "cluster_levels",
    "collect_swings",
    "fmt_price",
    "in_zone",
    "nearest_swing_before",
    "normalized_zone_width",
    "range_threshold",
    "ts_utc",
    "touched_zone_after",
    "zone_overlap",
]
