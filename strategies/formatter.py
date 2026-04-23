from __future__ import annotations

from market_primitives.common import fmt_price

from .types import EntrySetup


def build_strategy_reason_lines(setup: EntrySetup) -> list[str]:
    if setup.model_name == "Entry Model 3" and setup.context_timeframe:
        return [
            f"HTF {setup.context_timeframe} context",
            setup.reason,
        ]
    return [setup.reason]


def setup_to_alert(setup: EntrySetup) -> dict:
    return {
        "symbol": setup.symbol,
        "timeframe": setup.timeframe,
        "pattern": setup.model_name,
        "type": setup.model_name,
        "detail": build_setup_alert_text(setup),
        "direction": "Bullish" if setup.direction == "long" else "Bearish",
        "score": setup.score,
        "time": setup.timestamp,
        "entry_low": setup.entry_low,
        "entry_high": setup.entry_high,
        "invalidation": setup.invalidation,
        "level": setup.structure_level or setup.sweep_level,
        "sweep_level": setup.sweep_level,
        "structure_level": setup.structure_level,
        "context_timeframe": setup.context_timeframe,
        "setup": setup,
        "alert_kind": "strategy",
    }


def build_setup_alert_text(setup: EntrySetup) -> str:
    lines = []
    if setup.context_timeframe:
        lines.append(f"{setup.symbol}  HTF {setup.context_timeframe} / LTF {setup.timeframe}")
    else:
        lines.append(f"{setup.symbol}  {setup.timeframe}")
    lines.append(f"{setup.model_name}  {setup.direction.upper()}")
    lines.extend(build_strategy_reason_lines(setup))
    lines.append(f"Entry zone: {fmt_price(setup.entry_low)} - {fmt_price(setup.entry_high)}")
    lines.append(f"Invalidation: {fmt_price(setup.invalidation)}")
    lines.append(f"Score: {setup.score}/5")
    return "\n".join(lines)


__all__ = ["build_setup_alert_text", "setup_to_alert"]
