"""
visuals.py — chart generation for ICT pattern alerts.

Dependencies: mplfinance, pandas, matplotlib
Install: pip install mplfinance pandas matplotlib

Style: light, minimal — TradingView-like.
Patterns rendered as zones/lines directly on chart.
"""
import io
import asyncio
import logging

logger = logging.getLogger(__name__)

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot   as plt
import matplotlib.patches  as patches
import pandas              as pd
import mplfinance          as mpf
from datetime import datetime, timezone


# ══════════════════════════════════════════════════════════════════════════════
#  STYLE
# ══════════════════════════════════════════════════════════════════════════════

_STYLE = mpf.make_mpf_style(
    base_mpf_style="default",
    marketcolors=mpf.make_marketcolors(
        up="#26a69a",    down="#1a1a1a",
        wick={"up": "#26a69a", "down": "#1a1a1a"},
        edge={"up": "#26a69a", "down": "#1a1a1a"},
        volume={"up": "#b2dfdb", "down": "#bdbdbd"},
    ),
    gridstyle="dotted",
    gridcolor="#cccccc",
    facecolor="#f0f0f0",
    figcolor="#f0f0f0",
    edgecolor="#cccccc",
    rc={
        "axes.labelcolor":   "#888888",
        "xtick.color":       "#aaaaaa",
        "ytick.color":       "#888888",
        "ytick.labelsize":   8,
        "xtick.labelsize":   7,
        "axes.spines.top":   False,
        "axes.spines.left":  False,
        "font.family":       "monospace",
    },
)

# Pattern → (fill_color, line_color, alpha)
_ZONE_STYLE = {
    "FVG":   ("#2196f3", "#1565c0", 0.12),
    "IFVG":  ("#9c27b0", "#6a1b9a", 0.12),
    "OB":    ("#ff9800", "#e65100", 0.15),
    "CHoCH": ("#f44336", "#b71c1c", 0.00),
    "BOS":   ("#26a69a", "#00695c", 0.00),
    "Swings":("#607d8b", "#37474f", 0.00),
    "Sweeps":("#ff5722", "#bf360c", 0.00),
}
_DEFAULT_ZONE_STYLE = ("#607d8b", "#37474f", 0.10)

# Candles to show per timeframe
_CANDLE_COUNT = {
    "1m": 80, "3m": 80, "5m": 72, "15m": 64,
    "30m": 56, "1h": 48, "4h": 42, "1d": 30,
}


# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════

def _to_df(candles: list, timeframe: str) -> pd.DataFrame:
    n   = _CANDLE_COUNT.get(timeframe, 60)
    raw = candles[-n:]
    df  = pd.DataFrame(raw)
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    df = df.set_index("time")
    df.columns = [c.capitalize() for c in df.columns]
    return df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


# ══════════════════════════════════════════════════════════════════════════════
#  ZONE RENDERING
# ══════════════════════════════════════════════════════════════════════════════

def _draw_zones(ax, patterns: list, df: pd.DataFrame):
    """
    Draw ICT zones on the price axis.
    Zones (FVG, IFVG, OB): semi-transparent fill + dashed border lines.
    Levels (BOS, CHoCH, Swings, Sweeps): solid horizontal line + label.
    """
    n = len(df)

    for p in patterns:
        ptype                    = p.get("pattern", "")
        fill_c, line_c, alpha    = _ZONE_STYLE.get(ptype, _DEFAULT_ZONE_STYLE)
        direction                = p.get("direction", "")

        # ── Resolve price levels
        if ptype in ("FVG", "IFVG"):
            hi = p.get("gap_high")
            lo = p.get("gap_low")
        elif ptype == "OB":
            hi = p.get("ob_high")
            lo = p.get("ob_low")
        else:
            hi = p.get("level")
            lo = None

        if hi is None:
            continue

        # ── Zone (two levels)
        if lo is not None and abs(hi - lo) > 0 and alpha > 0:
            ax.axhspan(lo, hi, color=fill_c, alpha=alpha, zorder=1, linewidth=0)
            ax.axhline(hi, color=line_c, linewidth=0.8,
                       linestyle="--", alpha=0.6, zorder=2)
            ax.axhline(lo, color=line_c, linewidth=0.8,
                       linestyle="--", alpha=0.6, zorder=2)
            # Label box at right edge
            mid = (hi + lo) / 2
            ax.annotate(
                f" {ptype} ",
                xy=(n - 1, mid),
                fontsize=6.5,
                color="white",
                backgroundcolor=line_c,
                ha="right",
                va="center",
                zorder=5,
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor=line_c,
                    edgecolor="none",
                    alpha=0.85,
                ),
            )

        # ── Level (single line)
        else:
            label = f"{ptype} {'↑' if 'Bull' in direction else '↓' if 'Bear' in direction else ''}"
            ax.axhline(hi, color=line_c, linewidth=1.0,
                       linestyle="-", alpha=0.75, zorder=2)
            ax.annotate(
                f" {label.strip()} ",
                xy=(n - 1, hi),
                fontsize=6.5,
                color=line_c,
                ha="right",
                va="bottom",
                zorder=5,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  PRICE LABEL  (current price box on right axis — like TradingView)
# ══════════════════════════════════════════════════════════════════════════════

def _draw_price_label(ax, df: pd.DataFrame):
    last_close = df["Close"].iloc[-1]
    last_time  = df.index[-1]
    is_up      = df["Close"].iloc[-1] >= df["Open"].iloc[-1]
    bg_color   = "#26a69a" if is_up else "#ef5350"

    ax.annotate(
        f" {last_close:,.1f} ",
        xy=(len(df) - 0.5, last_close),
        fontsize=8,
        fontweight="bold",
        color="white",
        ha="left",
        va="center",
        zorder=10,
        annotation_clip=False,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor=bg_color,
            edgecolor="none",
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SYNC RENDER
# ══════════════════════════════════════════════════════════════════════════════

def _render(df: pd.DataFrame, patterns: list, symbol: str, timeframe: str) -> io.BytesIO:
    fig, axlist = mpf.plot(
        df,
        type="candle",
        style=_STYLE,
        title="",
        ylabel="",
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

    ax = axlist[0]

    # Draw pattern zones
    if patterns:
        _draw_zones(ax, patterns, df)

    # Current price label
    _draw_price_label(ax, df)

    # Clean title: symbol · tf top-left
    ax.set_title(
        f"{symbol}  ·  {timeframe}",
        loc="left",
        fontsize=10,
        color="#444444",
        pad=8,
        fontfamily="monospace",
    )

    # Remove y-axis label clutter
    ax.set_ylabel("")
    axlist[2].set_ylabel("")   # volume panel

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

async def generate_chart(candles: list, patterns: list,
                         symbol: str, timeframe: str) -> io.BytesIO | None:
    if not candles:
        return None
    try:
        df  = _to_df(candles, timeframe)
        buf = await asyncio.to_thread(_render, df, patterns, symbol, timeframe)
        return buf
    except Exception as e:
        logger.error(f"generate_chart {symbol} {timeframe}: {e}")
        return None
