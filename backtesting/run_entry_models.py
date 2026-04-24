from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from backtesting import BacktestResult, Candle
from backtesting.data import HistoricalDataError, find_history_file, load_candles, load_history_for
from backtesting.metrics import build_all_summaries
from backtesting.replay import ReplayWarning, normalize_model_key, replay_entry_models_multi_timeframe
from backtesting.report import write_reports
from scanner.engine import MODEL_3_HTF_MAP, MODEL_3_LTF_MAP

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        models = _selected_models(args)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    try:
        candle_store, warnings = _load_candle_store(
            data_dir=Path(args.data_dir),
            symbols=args.symbols,
            timeframes=args.timeframes,
            models=models,
        )
    except HistoricalDataError as exc:
        print(f"Error: {exc}")
        return 2

    all_results: list[BacktestResult] = []
    all_warnings = list(warnings)
    for symbol in args.symbols:
        for timeframe in args.timeframes:
            candles = candle_store.get((symbol, timeframe), [])
            if not candles:
                print(f"Error: no candles loaded for {symbol} {timeframe}")
                return 2
        results, replay_warnings = replay_entry_models_multi_timeframe(
            candle_store=candle_store,
            symbol=symbol,
            timeframes=args.timeframes,
            models=models,
            forward_bars=args.forward_bars,
            warmup_bars=args.warmup_bars,
            cooldown_bars=args.cooldown_bars,
            price_precision=args.price_precision,
            start_ms=_parse_time_ms(args.start, is_end=False) if args.start else None,
            end_ms=_parse_time_ms(args.end, is_end=True) if args.end else None,
        )
        all_results.extend(results)
        all_warnings.extend(replay_warnings)

    summaries = build_all_summaries(all_results)
    write_reports(
        out_dir=args.out_dir,
        results=all_results,
        summaries=summaries,
        warnings=all_warnings,
        config={
            "symbols": args.symbols,
            "timeframes": args.timeframes,
            "models": models,
            "warmup_bars": args.warmup_bars,
            "forward_bars": args.forward_bars,
            "cooldown_bars": args.cooldown_bars,
            "start": args.start,
            "end": args.end,
        },
    )

    print(f"Backtest complete: events={len(all_results)} warnings={len(all_warnings)} out_dir={args.out_dir}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline event-study backtest for Entry Model 1/2/3.")
    parser.add_argument("--data-dir", default="data/history", help="Directory with historical OHLCV CSV/JSON files.")
    parser.add_argument("--symbols", nargs="+", required=True, help="Symbols, e.g. BTCUSDT ETHUSDT.")
    parser.add_argument("--timeframes", nargs="+", required=True, help="Primary timeframes, e.g. 15m 1h.")
    parser.add_argument("--models", nargs="+", help="Models to run: model1 model2 model3.")
    parser.add_argument("--model", action="append", help="Single model selector. Can be repeated.")
    parser.add_argument("--forward-bars", type=int, default=20, help="Number of future bars for outcome evaluation.")
    parser.add_argument("--warmup-bars", type=int, default=100, help="Bars to skip before replay starts.")
    parser.add_argument("--cooldown-bars", type=int, default=5, help="Dedup cooldown for same rounded setup zone.")
    parser.add_argument("--price-precision", type=int, default=4, help="Precision used for rounded entry-zone dedup.")
    parser.add_argument("--start", help="UTC replay start datetime/date, e.g. 2025-05-01.")
    parser.add_argument("--end", help="UTC replay end datetime/date, e.g. 2025-06-30.")
    parser.add_argument("--out-dir", default="backtest_results", help="Output directory for CSV and markdown report.")
    return parser


def _selected_models(args: argparse.Namespace) -> list[str]:
    requested = []
    if args.models:
        requested.extend(args.models)
    if args.model:
        requested.extend(args.model)
    if not requested:
        requested = ["model1", "model2", "model3"]
    normalized: list[str] = []
    for item in requested:
        model = normalize_model_key(item)
        if model not in normalized:
            normalized.append(model)
    return normalized


def _load_candle_store(
    *,
    data_dir: Path,
    symbols: list[str],
    timeframes: list[str],
    models: list[str],
) -> tuple[dict[tuple[str, str], list[Candle]], list[ReplayWarning]]:
    store: dict[tuple[str, str], list[Candle]] = {}
    warnings: list[ReplayWarning] = []

    required = {(symbol, timeframe) for symbol in symbols for timeframe in timeframes}
    optional = _optional_context_keys(symbols, timeframes)

    for symbol, timeframe in sorted(required):
        store[(symbol, timeframe)] = load_history_for(data_dir, symbol, timeframe, required=True) or []

    for symbol, timeframe in sorted(optional - required):
        path = find_history_file(data_dir, symbol, timeframe)
        if path is not None:
            store[(symbol, timeframe)] = load_candles(path)

    if "model3" in models:
        for symbol in symbols:
            for timeframe in timeframes:
                htf = MODEL_3_HTF_MAP.get(timeframe)
                ltf = MODEL_3_LTF_MAP.get(timeframe)
                for context_tf, label in ((htf, "HTF"), (ltf, "LTF")):
                    if context_tf and (symbol, context_tf) not in store:
                        warnings.append(
                            ReplayWarning(
                                model_name="Entry Model 3",
                                symbol=symbol,
                                timeframe=timeframe,
                                timestamp=0,
                                message=f"missing optional {label} history {context_tf}; model3 context will be incomplete",
                            )
                        )
    return store, warnings


def _optional_context_keys(symbols: list[str], timeframes: list[str]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for symbol in symbols:
        for timeframe in timeframes:
            htf = MODEL_3_HTF_MAP.get(timeframe)
            ltf = MODEL_3_LTF_MAP.get(timeframe)
            if htf:
                keys.add((symbol, htf))
            if ltf:
                keys.add((symbol, ltf))
    return keys


def _parse_time_ms(value: str, *, is_end: bool) -> int:
    text = value.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        text = f"{text}T23:59:59.999+00:00" if is_end else f"{text}T00:00:00+00:00"
    elif text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


if __name__ == "__main__":
    raise SystemExit(main())
