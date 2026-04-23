from __future__ import annotations

from market_primitives.common import fmt_price

from .types import EntrySetup


def build_setup_alert_text(setup: EntrySetup) -> str:
    lines = []
    if setup.context_timeframe:
        lines.append(f"{setup.symbol}  HTF {setup.context_timeframe} / LTF {setup.timeframe}")
    else:
        lines.append(f"{setup.symbol}  {setup.timeframe}")
    lines.append(f"{setup.model_name}  {setup.direction.upper()}")
    lines.append(setup.reason)
    lines.append(f"Entry zone: {fmt_price(setup.entry_low)} - {fmt_price(setup.entry_high)}")
    lines.append(f"Invalidation: {fmt_price(setup.invalidation)}")
    lines.append(f"Score: {setup.score}/5")
    return "\n".join(lines)


def setup_to_alert(setup: EntrySetup):
    from presentation.alert_builders import from_entry_setup

    return from_entry_setup(setup)


__all__ = ["build_setup_alert_text", "setup_to_alert"]
