from __future__ import annotations

import unittest

from market_primitives.common import FairValueGap, LiquiditySweep, StructureBreak, SwingPoint
from market_primitives.displacement import evaluate_displacement
from market_primitives.fvg import detect_fvg
from market_primitives.ifvg import detect_ifvg
from strategies.entry_model_1 import detect_entry_model_1
from strategies.htf_context import HTFBias, HTFContext, HTFDealingRange, HTFObjective, HTFZone, build_htf_context
from strategies.types import PrimitiveSnapshot, StrategyContext


def candle(ts: int, open_: float, high: float, low: float, close: float) -> dict[str, float | int]:
    return {"time": ts, "open": open_, "high": high, "low": low, "close": close, "volume": 100.0}


def bullish_htf() -> HTFContext:
    return HTFContext(
        timeframe="1h",
        bias=HTFBias("bullish", 0.8, "test"),
        zone=HTFZone("OB", "bullish", 99, 101, 1, 0.8, "test"),
        dealing_range=HTFDealingRange(90, 110, 100, "discount"),
        objective=HTFObjective("up", 120, "swing_high", "test"),
        inside_zone=True,
        approaching_zone=True,
        allows_long=True,
        allows_short=False,
        score_modifier=0.0,
        reason="test",
    )


class ICTRefactorTests(unittest.TestCase):
    def test_displacement_strong_body_and_range_passes(self) -> None:
        candles = [
            candle(1, 100, 102, 99, 101),
            candle(2, 101, 103, 100, 102),
            candle(3, 102, 104, 101, 103),
            candle(4, 103, 120, 102, 118),
        ]

        quality = evaluate_displacement(candles, 3, direction="bullish", structure_level=110)

        self.assertTrue(quality.has_displacement)
        self.assertGreaterEqual(quality.body_ratio, 0.55)
        self.assertGreaterEqual(quality.range_expansion, 1.2)

    def test_displacement_weak_break_fails(self) -> None:
        candles = [
            candle(1, 100, 102, 99, 101),
            candle(2, 101, 103, 100, 102),
            candle(3, 102, 104, 101, 103),
            candle(4, 103, 105, 102, 104),
        ]

        quality = evaluate_displacement(candles, 3, direction="bullish", structure_level=103.5)

        self.assertFalse(quality.has_displacement)

    def test_fvg_lifecycle_tracks_partial_fill(self) -> None:
        candles = [
            candle(1, 96, 100, 95, 99),
            candle(2, 99, 101, 98, 100),
            candle(3, 103, 105, 102, 104),
            candle(4, 104, 105, 101, 103),
            candle(5, 103, 104, 102, 103),
        ]

        gaps = detect_fvg(candles, "BTCUSDT", "5m", scan_back=10)
        bullish = next(gap for gap in gaps if gap.direction == "bullish")

        self.assertEqual(bullish.status, "partially_filled")
        self.assertGreater(bullish.fill_percent, 0)
        self.assertEqual(bullish.consequent_encroachment, 101)

    def test_ifvg_requires_body_close_not_wick_only(self) -> None:
        wick_only = [
            candle(1, 105, 106, 100, 104),
            candle(2, 104, 105, 101, 103),
            candle(3, 99, 99, 94, 95),
            candle(4, 96, 105, 95, 99.5),
            candle(5, 100, 101, 99, 100),
        ]

        self.assertEqual(detect_ifvg(wick_only, "BTCUSDT", "5m"), [])

    def test_ifvg_bearish_source_breached_up_becomes_bullish(self) -> None:
        candles = [
            candle(1, 105, 106, 100, 104),
            candle(2, 104, 105, 101, 103),
            candle(3, 99, 99, 94, 95),
            candle(4, 96, 119, 95, 113),
            candle(5, 100, 101, 99, 100),
        ]

        ifvgs = detect_ifvg(candles, "BTCUSDT", "5m")

        self.assertEqual(len(ifvgs), 1)
        self.assertEqual(ifvgs[0].source_direction, "bearish")
        self.assertEqual(ifvgs[0].direction, "bullish")
        self.assertGreater(ifvgs[0].breach_displacement_factor, 0)

    def test_htf_objective_alone_does_not_create_bias(self) -> None:
        snapshot = PrimitiveSnapshot(
            symbol="BTCUSDT",
            timeframe="1h",
            candles=[candle(1, 100, 101, 99, 100), candle(2, 100, 101, 99, 100)],
            swings=[
                SwingPoint("BTCUSDT", "1h", "low", 1, 0, 90, 2, "intermediate", 0.7),
                SwingPoint("BTCUSDT", "1h", "high", 2, 1, 120, 2, "intermediate", 0.7),
            ],
        )

        context = build_htf_context(snapshot, current_price_value=100)

        self.assertEqual(context.objective.direction, "up")
        self.assertEqual(context.bias.direction, "neutral")

    def test_model1_rejects_sequence_without_displacement_when_required(self) -> None:
        snapshot = PrimitiveSnapshot(
            symbol="BTCUSDT",
            timeframe="5m",
            candles=[
                candle(1, 100, 101, 98, 100),
                candle(2, 100, 102, 99, 101),
                candle(3, 101, 103, 100, 102),
                candle(4, 102, 103, 100.5, 101),
            ],
            sweeps=[
                LiquiditySweep("BTCUSDT", "5m", "bullish", 1, 99, 98, 100, 0, True, 1.0, "short")
            ],
            structure_breaks=[
                StructureBreak("BTCUSDT", "5m", "MSS", "bullish", 2, 101, 102, 0, 0.4)
            ],
            fvgs=[
                FairValueGap("BTCUSDT", "5m", "bullish", 3, 100.5, 101.5, False, False, None, None, 0.0)
            ],
        )
        context = StrategyContext(primary=snapshot, htf_context=bullish_htf(), htf_mode="strict", require_displacement=True)

        self.assertEqual(detect_entry_model_1(context), [])


if __name__ == "__main__":
    unittest.main()
