from __future__ import annotations

from collections import defaultdict

from presentation.types import AlertPayload


def build_confluence_messages(symbol: str, alerts_by_timeframe: dict[str, list[AlertPayload]]) -> list[str]:
    signals: dict[tuple[str, str | None], list[str]] = defaultdict(list)
    for timeframe, alerts in alerts_by_timeframe.items():
        for alert in alerts:
            signals[(alert.pattern, alert.direction)].append(timeframe)

    messages = []
    for (pattern, direction), timeframes in signals.items():
        if len(timeframes) < 2:
            continue
        joined = " + ".join(sorted(timeframes))
        messages.append(f"{symbol} - CONFLUENCE: {pattern} {direction or ''} on {joined}".strip())
    return messages


__all__ = ["build_confluence_messages"]
