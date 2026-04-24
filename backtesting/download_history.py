from __future__ import annotations

import argparse
import asyncio
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp
from timeframes import SUPPORTED_TIMEFRAMES

BINANCE_FUTURES_API = "https://fapi.binance.com"
MAX_BINANCE_LIMIT = 1500


async def main_async(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download Binance Futures OHLCV history into backtest CSV files.")
    parser.add_argument("--out-dir", default="data/history")
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--timeframes", nargs="+", required=True, choices=SUPPORTED_TIMEFRAMES)
    parser.add_argument("--limit", type=int, default=1000, help="Candles per symbol/timeframe, max 1500 per request.")
    parser.add_argument("--start", help="UTC start datetime/date, e.g. 2024-11-06 or 2024-11-06T00:00:00Z.")
    parser.add_argument("--end", help="UTC end datetime/date, e.g. 2026-04-20 or 2026-04-20T23:59:59Z.")
    args = parser.parse_args(argv)

    limit = min(max(args.limit, 1), MAX_BINANCE_LIMIT)
    start_ms = parse_time_ms(args.start, is_end=False) if args.start else None
    end_ms = parse_time_ms(args.end, is_end=True) if args.end else None
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
        for symbol in args.symbols:
            for timeframe in args.timeframes:
                candles = await fetch_history(session, symbol, timeframe, limit, start_ms, end_ms)
                if not candles:
                    print(f"SKIP {symbol} {timeframe}: no candles returned")
                    continue
                path = out_dir / f"{symbol}_{timeframe}.csv"
                write_csv(path, candles)
                print(f"Wrote {len(candles)} candles: {path}")
    return 0


async def fetch_history(
    session: aiohttp.ClientSession,
    symbol: str,
    interval: str,
    limit: int,
    start_ms: int | None,
    end_ms: int | None,
) -> list[dict[str, float | int]]:
    if start_ms is None:
        return await fetch_klines(session, symbol, interval, limit, None, end_ms)

    all_candles: list[dict[str, float | int]] = []
    next_start = start_ms
    while True:
        batch = await fetch_klines(session, symbol, interval, limit, next_start, end_ms)
        if not batch:
            break
        all_candles.extend(batch)
        last_open = int(batch[-1]["time"])
        if end_ms is not None and last_open >= end_ms:
            break
        if len(batch) < limit:
            break
        next_start = last_open + 1
        await asyncio.sleep(0.05)

    deduped = {int(candle["time"]): candle for candle in all_candles}
    return [deduped[key] for key in sorted(deduped)]


async def fetch_klines(
    session: aiohttp.ClientSession,
    symbol: str,
    interval: str,
    limit: int,
    start_ms: int | None,
    end_ms: int | None,
) -> list[dict[str, float | int]]:
    url = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    if start_ms is not None:
        params["startTime"] = start_ms
    if end_ms is not None:
        params["endTime"] = end_ms
    async with session.get(url, params=params) as response:
        payload: Any = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Binance error {response.status} for {symbol} {interval}: {payload}")
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected Binance payload for {symbol} {interval}: {payload}")
    return [
        {
            "time": int(item[0]),
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
        }
        for item in payload
    ]


def write_csv(path: Path, candles: list[dict[str, float | int]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(candles)


def parse_time_ms(value: str, *, is_end: bool) -> int:
    text = value.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        text = f"{text}T23:59:59.999+00:00" if is_end else f"{text}T00:00:00+00:00"
    elif text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(main_async(argv))


if __name__ == "__main__":
    raise SystemExit(main())
