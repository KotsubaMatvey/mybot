from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any, Callable

from backtesting import BacktestResult

SummaryRow = dict[str, Any]
KeyFunc = Callable[[BacktestResult], tuple[Any, ...]]


def score_bucket(score: int | None) -> str:
    if score is None:
        return "unknown"
    if score <= 2:
        return "low"
    if score == 3:
        return "medium"
    return "high"


def build_all_summaries(results: list[BacktestResult]) -> dict[str, list[SummaryRow]]:
    return {
        "summary_by_model": summarize(results, lambda row: (row.event.model_name,), ("model",)),
        "summary_by_direction": summarize(
            results,
            lambda row: (row.event.model_name, row.event.direction),
            ("model", "direction"),
        ),
        "summary_by_timeframe": summarize(
            results,
            lambda row: (row.event.model_name, row.event.timeframe),
            ("model", "timeframe"),
        ),
        "summary_by_symbol": summarize(
            results,
            lambda row: (row.event.model_name, row.event.symbol),
            ("model", "symbol"),
        ),
        "summary_by_score": summarize(
            results,
            lambda row: (row.event.model_name, score_bucket(row.event.score)),
            ("model", "score_bucket"),
        ),
    }


def summarize(results: list[BacktestResult], key_func: KeyFunc, key_names: tuple[str, ...]) -> list[SummaryRow]:
    grouped: dict[tuple[Any, ...], list[BacktestResult]] = defaultdict(list)
    for result in results:
        grouped[key_func(result)].append(result)

    rows: list[SummaryRow] = []
    for key, group in sorted(grouped.items(), key=lambda item: tuple(str(part) for part in item[0])):
        row: SummaryRow = {name: value for name, value in zip(key_names, key)}
        row.update(_metrics_for(group))
        rows.append(row)
    return rows


def _metrics_for(group: list[BacktestResult]) -> SummaryRow:
    count = len(group)
    valid_r = [item for item in group if item.event.skipped_reason is None and item.outcome.mfe_r is not None]
    mfe_r = [item.outcome.mfe_r for item in valid_r if item.outcome.mfe_r is not None]
    mae_r = [item.outcome.mae_r for item in valid_r if item.outcome.mae_r is not None]
    scores = [item.event.score for item in group if item.event.score is not None]

    return {
        "count": count,
        "valid_outcome_count": len(valid_r),
        "skipped_outcome_count": sum(1 for item in group if item.event.skipped_reason is not None),
        "long_count": sum(1 for item in group if item.event.direction == "long"),
        "short_count": sum(1 for item in group if item.event.direction == "short"),
        "avg_mfe_r": _avg(mfe_r),
        "median_mfe_r": _median(mfe_r),
        "avg_mae_r": _avg(mae_r),
        "median_mae_r": _median(mae_r),
        "hit_0_5r_rate": _rate(valid_r, lambda item: item.outcome.hit_0_5r),
        "hit_1r_rate": _rate(valid_r, lambda item: item.outcome.hit_1r),
        "hit_2r_rate": _rate(valid_r, lambda item: item.outcome.hit_2r),
        "invalidation_rate": _rate(group, lambda item: item.outcome.invalidated),
        "hit_1r_before_invalidation_rate": _rate(valid_r, lambda item: item.outcome.hit_1r_before_invalidation),
        "hit_2r_before_invalidation_rate": _rate(valid_r, lambda item: item.outcome.hit_2r_before_invalidation),
        "avg_score": _avg(scores),
        "best_symbol": _best_dimension(group, "symbol"),
        "best_timeframe": _best_dimension(group, "timeframe"),
    }


def _avg(values: list[float | int]) -> float | None:
    if not values:
        return None
    return round(sum(float(value) for value in values) / len(values), 6)


def _median(values: list[float | int]) -> float | None:
    if not values:
        return None
    return round(float(median(float(value) for value in values)), 6)


def _rate(group: list[BacktestResult], predicate: Callable[[BacktestResult], bool]) -> float | None:
    if not group:
        return None
    return round(sum(1 for item in group if predicate(item)) / len(group), 6)


def _best_dimension(group: list[BacktestResult], attr: str) -> str | None:
    by_value: dict[str, list[float]] = defaultdict(list)
    for item in group:
        value = str(getattr(item.event, attr))
        if item.outcome.mfe_r is not None:
            by_value[value].append(item.outcome.mfe_r)
    if not by_value:
        return None
    best = max(by_value.items(), key=lambda item: sum(item[1]) / len(item[1]))
    return best[0]


__all__ = ["SummaryRow", "build_all_summaries", "score_bucket", "summarize"]
