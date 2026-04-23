"""Chart generation for primitive and strategy alerts."""
from __future__ import annotations

import asyncio
import io
import logging

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from presentation.chart_payloads import visible_alerts_for_chart
from presentation.types import AlertPayload

logger = logging.getLogger(__name__)

_STYLE = mpf.make_mpf_style(
    base_mpf_style="default",
    marketcolors=mpf.make_marketcolors(
        up="#0f766e",
        down="#9f1239",
        wick={"up": "#0f766e", "down": "#9f1239"},
        edge={"up": "#0f766e", "down": "#9f1239"},
        volume={"up": "#99f6e4", "down": "#fda4af"},
    ),
    gridstyle="dotted",
    gridcolor="#d4d4d8",
    facecolor="#fafaf9",
    figcolor="#fafaf9",
    rc={"font.family": "monospace", "ytick.labelsize": 8, "xtick.labelsize": 7},
)

_ZONE_STYLE = {
    "FVG": ("#2563eb", "#1d4ed8", 0.12),
    "IFVG": ("#7c3aed", "#6d28d9", 0.12),
    "OB": ("#f59e0b", "#b45309", 0.14),
    "Breaker": ("#ef4444", "#b91c1c", 0.14),
    "Entry Model 1": ("#14b8a6", "#0f766e", 0.16),
    "Entry Model 2": ("#f97316", "#c2410c", 0.18),
    "Entry Model 3": ("#0ea5e9", "#0369a1", 0.18),
}
_LEVEL_STYLE = {
    "BOS": "#0f766e",
    "CHoCH": "#be123c",
    "Swings": "#475569",
    "Sweeps": "#ea580c",
    "Liquidity": "#dc2626",
    "KL": "#334155",
    "SMT": "#7c3aed",
}
_CANDLE_COUNT = {"1m": 90, "5m": 72, "15m": 64, "30m": 56, "1h": 48, "4h": 42, "1d": 30}


def _to_df(candles: list[dict], timeframe: str) -> pd.DataFrame:
    raw = candles[-_CANDLE_COUNT.get(timeframe, 60) :]
    frame = pd.DataFrame(raw)
    frame["time"] = pd.to_datetime(frame["time"], unit="ms", utc=True)
    frame = frame.set_index("time")
    frame.columns = [name.capitalize() for name in frame.columns]
    return frame[["Open", "High", "Low", "Close", "Volume"]].astype(float)


def _draw_patterns(ax, patterns: list[AlertPayload], n: int) -> None:
    for pattern in patterns:
        if pattern.alert_kind == "strategy":
            _draw_setup(ax, pattern, n)
            continue

        if pattern.pattern in {"FVG", "IFVG"} and pattern.gap_low is not None and pattern.gap_high is not None:
            fill_color, line_color, alpha = _ZONE_STYLE.get(pattern.pattern, ("#64748b", "#334155", 0.12))
            ax.axhspan(pattern.gap_low, pattern.gap_high, color=fill_color, alpha=alpha, zorder=1, linewidth=0)
            ax.axhline(pattern.gap_low, color=line_color, linestyle="--", linewidth=0.8)
            ax.axhline(pattern.gap_high, color=line_color, linestyle="--", linewidth=0.8)
            ax.text(n - 1, (pattern.gap_low + pattern.gap_high) / 2, f" {pattern.pattern} ", ha="right", va="center", color="white", fontsize=6.5, backgroundcolor=line_color)
            continue

        if pattern.pattern in {"OB", "Breaker"} and pattern.ob_low is not None and pattern.ob_high is not None:
            fill_color, line_color, alpha = _ZONE_STYLE.get(pattern.pattern, ("#64748b", "#334155", 0.12))
            ax.axhspan(pattern.ob_low, pattern.ob_high, color=fill_color, alpha=alpha, zorder=1, linewidth=0)
            ax.axhline(pattern.ob_low, color=line_color, linestyle="--", linewidth=0.8)
            ax.axhline(pattern.ob_high, color=line_color, linestyle="--", linewidth=0.8)
            ax.text(n - 1, (pattern.ob_low + pattern.ob_high) / 2, f" {pattern.pattern} ", ha="right", va="center", color="white", fontsize=6.5, backgroundcolor=line_color)
            continue

        if pattern.level is None:
            continue
        color = _LEVEL_STYLE.get(pattern.pattern, "#334155")
        ax.axhline(pattern.level, color=color, linewidth=1.0, alpha=0.75)
        ax.text(n - 1, pattern.level, f" {pattern.pattern} ", ha="right", va="bottom", fontsize=6.5, color=color)


def _draw_setup(ax, pattern: AlertPayload, n: int) -> None:
    if pattern.entry_low is None or pattern.entry_high is None:
        return

    fill_color, line_color, alpha = _ZONE_STYLE.get(pattern.pattern, ("#0f766e", "#0f766e", 0.16))
    ax.axhspan(pattern.entry_low, pattern.entry_high, color=fill_color, alpha=alpha, zorder=1, linewidth=0)
    ax.axhline(pattern.entry_low, color=line_color, linestyle="--", linewidth=1.0)
    ax.axhline(pattern.entry_high, color=line_color, linestyle="--", linewidth=1.0)
    ax.text(n - 1, (pattern.entry_low + pattern.entry_high) / 2, f" {pattern.pattern} ", ha="right", va="center", color="white", fontsize=6.5, backgroundcolor=line_color)

    if pattern.invalidation is not None:
        ax.axhline(pattern.invalidation, color="#991b1b", linestyle=":", linewidth=1.0)
        ax.text(n - 1, pattern.invalidation, " invalidation ", ha="right", va="top", fontsize=6.0, color="#991b1b")
    if pattern.sweep_level is not None:
        ax.axhline(pattern.sweep_level, color="#ea580c", linestyle="-.", linewidth=0.9, alpha=0.7)
    if pattern.structure_level is not None:
        ax.axhline(pattern.structure_level, color="#0f766e", linestyle="-.", linewidth=0.9, alpha=0.7)


def _draw_price_label(ax, frame: pd.DataFrame) -> None:
    last_close = frame["Close"].iloc[-1]
    is_up = frame["Close"].iloc[-1] >= frame["Open"].iloc[-1]
    color = "#0f766e" if is_up else "#9f1239"
    ax.annotate(
        f" {last_close:,.1f} ",
        xy=(len(frame) - 0.5, last_close),
        ha="left",
        va="center",
        fontsize=8,
        color="white",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "edgecolor": "none"},
    )


def _render(frame: pd.DataFrame, patterns: list[AlertPayload], symbol: str, timeframe: str) -> io.BytesIO:
    fig, axes = mpf.plot(
        frame,
        type="candle",
        style=_STYLE,
        volume=True,
        volume_panel=1,
        panel_ratios=(5, 1),
        returnfig=True,
        figsize=(10, 5.5),
        tight_layout=True,
        xrotation=0,
        datetime_format="%H:%M",
        scale_padding={"left": 0.1, "right": 1.2, "top": 0.3, "bottom": 0.5},
    )
    ax = axes[0]
    visible_patterns = visible_alerts_for_chart(
        [
            {
                "low": float(row["Low"]),
                "high": float(row["High"]),
            }
            for _, row in frame.iterrows()
        ],
        patterns,
    )
    if visible_patterns:
        _draw_patterns(ax, visible_patterns, len(frame))
    _draw_price_label(ax, frame)
    ax.set_title(f"{symbol}  {timeframe}", loc="left", fontsize=10, color="#334155", pad=8)
    ax.set_ylabel("")
    axes[2].set_ylabel("")

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
    buffer.seek(0)
    plt.close(fig)
    return buffer


async def generate_chart(candles: list[dict], patterns: list[AlertPayload], symbol: str, timeframe: str) -> io.BytesIO | None:
    if not candles:
        return None
    try:
        frame = _to_df(candles, timeframe)
        return await asyncio.to_thread(_render, frame, patterns or [], symbol, timeframe)
    except Exception as exc:
        logger.error("generate_chart %s %s: %s", symbol, timeframe, exc)
        return None


__all__ = ["generate_chart"]
