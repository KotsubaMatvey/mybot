from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backtesting import BacktestResult
from backtesting.metrics import SummaryRow
from backtesting.replay import ReplayWarning


def write_reports(
    *,
    out_dir: str | Path,
    results: list[BacktestResult],
    summaries: dict[str, list[SummaryRow]],
    warnings: list[ReplayWarning],
    config: dict[str, Any],
) -> None:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    _write_events_csv(target / "events.csv", results)
    for name, rows in summaries.items():
        _write_rows_csv(target / f"{name}.csv", rows, fieldnames=_summary_fieldnames(name, rows))
    _write_report_md(target / "report.md", results, summaries, warnings, config)


def _write_events_csv(path: Path, results: list[BacktestResult]) -> None:
    rows = [_flatten_result(result) for result in results]
    fieldnames = list(rows[0].keys()) if rows else _empty_event_fieldnames()
    _write_rows_csv(path, rows, fieldnames=fieldnames)


def _write_rows_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def _write_report_md(
    path: Path,
    results: list[BacktestResult],
    summaries: dict[str, list[SummaryRow]],
    warnings: list[ReplayWarning],
    config: dict[str, Any],
) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    skipped = [result for result in results if result.event.skipped_reason]
    lines = [
        "# Entry Models Backtest Report",
        "",
        "Config:",
        f"- symbols: {', '.join(config.get('symbols', []))}",
        f"- timeframes: {', '.join(config.get('timeframes', []))}",
        f"- models: {', '.join(config.get('models', []))}",
        f"- warmup_bars: {config.get('warmup_bars')}",
        f"- forward_bars: {config.get('forward_bars')}",
        f"- cooldown_bars: {config.get('cooldown_bars')}",
        f"- start: {config.get('start') or 'full history'}",
        f"- end: {config.get('end') or 'full history'}",
        f"- generated_at: {generated_at}",
        "",
        "This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.",
        "",
        "## 1. Overall summary",
        f"- events: {len(results)}",
        f"- warnings: {len(warnings)}",
        f"- skipped_outcome_events: {len(skipped)}",
        "",
        "## 2. Summary by model",
        _markdown_table(summaries.get("summary_by_model", [])),
        "",
        "## 3. Summary by direction",
        _markdown_table(summaries.get("summary_by_direction", [])),
        "",
        "## 4. Summary by timeframe",
        _markdown_table(summaries.get("summary_by_timeframe", [])),
        "",
        "## 5. Score bucket analysis",
        _markdown_table(summaries.get("summary_by_score", [])),
        "",
        "## 6. Warnings / skipped events",
    ]
    if warnings:
        lines.extend(f"- {item.model_name} {item.symbol} {item.timeframe} {item.timestamp}: {item.message}" for item in warnings[:50])
    if skipped:
        lines.extend(f"- {item.event.event_id}: {item.event.skipped_reason} ({item.event.warning or 'no warning'})" for item in skipped[:50])
    if not warnings and not skipped:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## 7. Interpretation notes",
            "- Replay is bar-by-bar: strategies receive only candles visible at the current bar.",
            "- Forward candles are used only after event detection for outcome measurement.",
            "- `bars_to_*` values are 1-based future bar offsets from the signal bar.",
            "- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _flatten_result(result: BacktestResult) -> dict[str, Any]:
    event = asdict(result.event)
    outcome = asdict(result.outcome)
    outcome.pop("event_id", None)
    return {**event, **outcome}


def _empty_event_fieldnames() -> list[str]:
    return [
        "event_id",
        "model_name",
        "symbol",
        "timeframe",
        "direction",
        "detected_at",
        "status",
        "entry_low",
        "entry_high",
        "entry_price",
        "invalidation",
        "risk",
        "score",
        "reason",
        "components_json",
        "warning",
        "skipped_reason",
        "forward_bars",
        "mfe",
        "mae",
        "mfe_r",
        "mae_r",
        "hit_0_5r",
        "hit_1r",
        "hit_2r",
        "invalidated",
        "bars_to_0_5r",
        "bars_to_1r",
        "bars_to_2r",
        "bars_to_invalidation",
        "future_high",
        "future_low",
        "hit_1r_before_invalidation",
        "hit_2r_before_invalidation",
    ]


def _summary_fieldnames(name: str, rows: list[SummaryRow]) -> list[str]:
    if rows:
        return list(rows[0].keys())
    prefix_by_name = {
        "summary_by_model": ["model"],
        "summary_by_direction": ["model", "direction"],
        "summary_by_timeframe": ["model", "timeframe"],
        "summary_by_symbol": ["model", "symbol"],
        "summary_by_score": ["model", "score_bucket"],
    }
    return prefix_by_name.get(name, []) + [
        "count",
        "valid_outcome_count",
        "skipped_outcome_count",
        "long_count",
        "short_count",
        "avg_mfe_r",
        "median_mfe_r",
        "avg_mae_r",
        "median_mae_r",
        "hit_0_5r_rate",
        "hit_1r_rate",
        "hit_2r_rate",
        "invalidation_rate",
        "hit_1r_before_invalidation_rate",
        "hit_2r_before_invalidation_rate",
        "avg_score",
        "best_symbol",
        "best_timeframe",
    ]


def _csv_value(value: Any) -> Any:
    return "" if value is None else value


def _markdown_table(rows: list[SummaryRow], limit: int = 12) -> str:
    if not rows:
        return "_No rows._"
    headers = list(rows[0].keys())
    visible = rows[:limit]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in visible:
        lines.append("| " + " | ".join(str(_csv_value(row.get(header))) for header in headers) + " |")
    if len(rows) > limit:
        lines.append(f"\n_Showing {limit} of {len(rows)} rows._")
    return "\n".join(lines)


__all__ = ["write_reports"]
