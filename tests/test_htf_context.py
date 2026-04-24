from __future__ import annotations

import unittest

from backtesting.context import build_strategy_context_for_replay
from market_primitives.common import StructureBreak, SwingPoint
from strategies.entry_model_1 import detect_entry_model_1
from strategies.entry_model_2 import detect_entry_model_2
from strategies.entry_model_3 import detect_entry_model_3
from strategies.htf_context import HTFBias, HTFContext, HTFDealingRange, HTFObjective, HTFZone, build_htf_context
from strategies.types import PrimitiveSnapshot, StrategyContext


def candle(ts: int, price: float) -> dict[str, float | int]:
    return {
        "time": ts,
        "open": price,
        "high": price + 1,
        "low": price - 1,
        "close": price,
        "volume": 100.0,
    }


class HTFContextTests(unittest.TestCase):
    def test_context_builder_slices_htf_by_timestamp(self) -> None:
        current_ts = 1_700_000_600_000
        primary = [candle(1_700_000_000_000, 100), candle(current_ts, 101)]
        store = {
            ("BTCUSDT", "5m"): primary,
            ("BTCUSDT", "1h"): [
                candle(1_700_000_000_000, 100),
                candle(current_ts, 101),
                candle(current_ts + 60_000, 120),
            ],
        }

        context = build_strategy_context_for_replay(
            symbol="BTCUSDT",
            timeframe="5m",
            primary_visible=primary,
            current_timestamp=current_ts,
            candle_store=store,
            htf_mode="strict",
        )

        self.assertIsNotNone(context.higher_timeframe)
        assert context.higher_timeframe is not None
        self.assertTrue(all(int(item["time"]) <= current_ts for item in context.higher_timeframe.candles))
        self.assertIsNotNone(context.htf_context)

    def test_build_htf_context_from_structure_and_range(self) -> None:
        snapshot = PrimitiveSnapshot(
            symbol="BTCUSDT",
            timeframe="1h",
            candles=[candle(1_700_000_000_000, 100), candle(1_700_000_300_000, 102)],
            swings=[
                SwingPoint("BTCUSDT", "1h", "low", 1_700_000_000_000, 0, 95, 2),
                SwingPoint("BTCUSDT", "1h", "high", 1_700_000_300_000, 1, 110, 2),
            ],
            structure_breaks=[
                StructureBreak("BTCUSDT", "1h", "BOS", "bullish", 1_700_000_300_000, 105, 106, 0, 0.8)
            ],
        )

        context = build_htf_context(snapshot, current_price_value=100)

        self.assertEqual(context.bias.direction, "bullish")
        self.assertIn(context.dealing_range.location, {"discount", "equilibrium"})

    def test_model1_strict_returns_no_setup_without_htf_context(self) -> None:
        snapshot = PrimitiveSnapshot("BTCUSDT", "5m", [candle(1_700_000_000_000, 100)])
        context = StrategyContext(primary=snapshot, htf_mode="strict")

        self.assertEqual(detect_entry_model_1(context), [])

    def test_model2_blocks_opposite_htf_bias(self) -> None:
        snapshot = PrimitiveSnapshot("BTCUSDT", "5m", [candle(1_700_000_000_000, 100)])
        htf = HTFContext(
            timeframe="1h",
            bias=HTFBias("bearish", 0.8, "test"),
            zone=HTFZone("OB", "bearish", 101, 103, 1_700_000_000_000, 0.8, "test"),
            dealing_range=HTFDealingRange(90, 110, 100, "premium"),
            objective=HTFObjective("down", 90, "swing_low", "test"),
            inside_zone=True,
            approaching_zone=True,
            allows_long=False,
            allows_short=True,
            score_modifier=0.0,
            reason="test",
        )
        context = StrategyContext(primary=snapshot, htf_context=htf, htf_mode="strict")

        self.assertEqual(detect_entry_model_2(context), [])

    def test_model3_requires_htf_and_ltf_context(self) -> None:
        snapshot = PrimitiveSnapshot("BTCUSDT", "5m", [candle(1_700_000_000_000, 100)])
        context = StrategyContext(primary=snapshot, htf_mode="strict")

        self.assertEqual(detect_entry_model_3(context), [])


if __name__ == "__main__":
    unittest.main()
