from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backtesting import Candle


class HistoricalDataError(Exception):
    """Raised when historical candle files are missing or malformed."""


def normalize_time_ms(value: Any) -> int:
    if isinstance(value, (int, float)):
        numeric = float(value)
    else:
        text = str(value).strip()
        if not text:
            raise ValueError("empty time value")
        try:
            numeric = float(text)
        except ValueError:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp() * 1000)

    if numeric < 10_000_000_000:
        numeric *= 1000
    return int(numeric)


def normalize_candle(row: dict[str, Any]) -> Candle:
    try:
        return {
            "time": normalize_time_ms(row["time"]),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row.get("volume", 0.0)),
        }
    except KeyError as exc:
        raise HistoricalDataError(f"missing candle column: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise HistoricalDataError(f"invalid candle row {row!r}: {type(exc).__name__}: {exc}") from exc


def candidate_paths(data_dir: str | Path, symbol: str, timeframe: str) -> list[Path]:
    base = Path(data_dir)
    return [
        base / f"{symbol}_{timeframe}.csv",
        base / f"{symbol}-{timeframe}.csv",
        base / symbol / f"{timeframe}.csv",
        base / f"{symbol}_{timeframe}.json",
        base / f"{symbol}-{timeframe}.json",
        base / symbol / f"{timeframe}.json",
    ]


def find_history_file(data_dir: str | Path, symbol: str, timeframe: str) -> Path | None:
    for path in candidate_paths(data_dir, symbol, timeframe):
        if path.exists() and path.is_file():
            return path
    return None


def load_candles(path: str | Path) -> list[Candle]:
    source = Path(path)
    if not source.exists():
        raise HistoricalDataError(f"history file does not exist: {source}")

    if source.suffix.lower() == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    elif source.suffix.lower() == ".json":
        with source.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise HistoricalDataError(f"JSON history must be a list of candles: {source}")
        rows = payload
    else:
        raise HistoricalDataError(f"unsupported history file type: {source.suffix}")

    candles = [normalize_candle(dict(row)) for row in rows]
    candles.sort(key=lambda candle: int(candle["time"]))
    return candles


def load_history_for(
    data_dir: str | Path,
    symbol: str,
    timeframe: str,
    *,
    required: bool = True,
) -> list[Candle] | None:
    path = find_history_file(data_dir, symbol, timeframe)
    if path is None:
        if required:
            patterns = ", ".join(str(item) for item in candidate_paths(data_dir, symbol, timeframe)[:3])
            raise HistoricalDataError(f"missing history for {symbol} {timeframe}; tried {patterns}")
        return None
    candles = load_candles(path)
    if required and not candles:
        raise HistoricalDataError(f"empty history file for {symbol} {timeframe}: {path}")
    return candles


__all__ = [
    "HistoricalDataError",
    "candidate_paths",
    "find_history_file",
    "load_candles",
    "load_history_for",
    "normalize_candle",
    "normalize_time_ms",
]
