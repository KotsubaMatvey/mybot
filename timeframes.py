from __future__ import annotations

SUPPORTED_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d"]

EXECUTION_HTF_MAP: dict[str, str] = {
    "1m": "15m",
    "3m": "30m",
    "5m": "1h",
    "15m": "4h",
    "30m": "4h",
    "1h": "1d",
}

MODEL_3_HTF_MAP: dict[str, str | None] = {
    "1m": "15m",
    "3m": "30m",
    "5m": "1h",
    "15m": "4h",
    "30m": "4h",
    "1h": "1d",
    "4h": "1d",
}

MODEL_3_LTF_MAP: dict[str, str | None] = {
    "5m": "1m",
    "15m": "3m",
    "30m": "5m",
    "1h": "15m",
    "4h": "1h",
}


def execution_htf_for(timeframe: str) -> str | None:
    return EXECUTION_HTF_MAP.get(timeframe) or MODEL_3_HTF_MAP.get(timeframe)


__all__ = [
    "EXECUTION_HTF_MAP",
    "MODEL_3_HTF_MAP",
    "MODEL_3_LTF_MAP",
    "SUPPORTED_TIMEFRAMES",
    "execution_htf_for",
]
