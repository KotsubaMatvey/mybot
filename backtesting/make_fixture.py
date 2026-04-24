from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a small synthetic OHLCV fixture for backtesting smoke tests.")
    parser.add_argument("--out-dir", default="tests/fixtures")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--timeframe", default="15m")
    parser.add_argument("--bars", type=int, default=180)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{args.symbol}_{args.timeframe}.csv"
    candles = _synthetic_candles(args.bars)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(candles)
    print(f"Wrote {len(candles)} candles to {path}")
    return 0


def _synthetic_candles(count: int) -> list[dict[str, float | int]]:
    candles: list[dict[str, float | int]] = []
    ts = 1_700_000_000_000
    price = 100.0
    step_ms = 15 * 60_000
    for index in range(count):
        wave = ((index % 18) - 9) * 0.12
        impulse = 1.8 if index in {70, 71, 72, 120, 121} else 0.0
        flush = -2.2 if index in {95, 96} else 0.0
        open_ = price
        close = price + wave * 0.2 + impulse + flush
        high = max(open_, close) + 0.55 + abs(wave) * 0.05
        low = min(open_, close) - 0.55 - abs(wave) * 0.05
        volume = 100.0 + (index % 12) * 7.0 + (80.0 if index in {95, 96, 120, 121} else 0.0)
        candles.append(
            {
                "time": ts + index * step_ms,
                "open": round(open_, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "close": round(close, 4),
                "volume": round(volume, 4),
            }
        )
        price = close
    return candles


if __name__ == "__main__":
    raise SystemExit(main())
