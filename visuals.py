"""
visuals.py — chart generation for ICT pattern alerts.

Dependencies: mplfinance, pandas, matplotlib
Install: pip install mplfinance pandas

Design decisions:
  - matplotlib backend set to Agg at import time (no display needed on VPS)
  - charts rendered to io.BytesIO — never touch disk
  - plt.close(fig) after each render — no memory leak
  - generation always via asyncio.to_thread — never blocks event loop
  - candle count scaled by timeframe, not fixed number
"""
import io
import asyncio
import logging
from datetime import timezone, datetime

logger = logging.getLogger(__name__)

# Must be set before any other matplotlib import
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot    as plt
import matplotlib.patches   as mpatches
import matplotlib.ticker    as mticker
import pandas               as pd
import mplfinance           as mpf


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# How many candles to show per timeframe — enough context, not a hairball
_CANDLE_COUNT = {
    "1m":  80,
    "3m":  80,
    "5m":  72,   # ~6h
    "15m": 64,   # ~16h
    "30m": 56,   # ~28h
    "1h":  48,   # 2 days
    "4h":  42,   # 7 days
    "1d":  30,   # 1 month
}
_DEFAULT_CANDLES = 60

_DARK_STYLE = mpf.make_mpf_style(
    base_mpf_style="nightclouds",
    gridstyle="dotted",
    gridcolor="#2a2a2a",
    facecolor="#0f0f0f",
    figcolor="#0f0f0f",
    edgecolor="#333333",
    marketcolors=mpf.make_marketcolors(
        up="#26a69a",   down="#ef5350",
        wick={"up": "#26a69a", "down": "#ef5350"},
        edge={"up": "#26a69a", "down": "#ef5350"},
        volume={"up": "#1a5c58", "down": "#7a2020"},
    ),
    rc={
        "axes.labelcolor":  "#888888",
        "xtick.color":      "#666666",
        "ytick.color":      "#666666",
        "axes.titlecolor":  "#cccccc",
        "font.size":        9,
    },
)

# Pattern type → zone colour
_ZONE_COLORS = {
    "OB":    ("#ff9800", 0.25),   # orange
    "FVG":   ("#2196f3", 0.20),   # blue
    "IFVG":  ("#9c27b0", 0.20),   # purple
    "CHoCH": ("#f44336", 0.00),   # red  (line only)
    "BOS":   ("#4caf50", 0.00),   # green (line only)
}
_DEFAULT_ZONE_COLOR = ("#607d8b", 0.20)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA PREP
# ══════════════════════════════════════════════════════════════════════════════

def candles_to_df(candles: list, timeframe: str) -> pd.DataFrame:
    """
    Convert scanner candle list to mplfinance-compatible DataFrame.
    candles: list of dicts with keys time, open, high, low, close, volume
    """
    n   = _CANDLE_COUNT.get(timeframe, _DEFAULT_CANDLES)
    raw = candles[-n:]

    df = pd.DataFrame(raw)
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    df = df.set_index("time")
    df.columns = [c.capitalize() for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  ZONE OVERLAYS
# ══════════════════════════════════════════════════════════════════════════════

def _add_zones(ax, patterns_meta: list, df: pd.DataFrame):
    """
    Draw zone overlays on the price axis based on detected patterns.
    Reads alert dicts from scanner — fields: gap_low/gap_high, ob_low/ob_high, level.
    """
    for p in patterns_meta:
        ptype        = p.get("pattern", "")
        color, alpha = _ZONE_COLORS.get(ptype, _DEFAULT_ZONE_COLOR)

        # Resolve high/low depending on pattern type
        if ptype in ("FVG", "IFVG"):
            hi = p.get("gap_high")
            lo = p.get("gap_low")
        elif ptype in ("OB",):
            hi = p.get("ob_high")
            lo = p.get("ob_low")
        else:
            # BOS, CHoCH, Swings, Sweeps — single level
            hi = p.get("level")
            lo = None

        if hi is None:
            continue

        if lo is not None and lo != hi and alpha > 0:
            ax.axhspan(lo, hi, color=color, alpha=alpha, zorder=1)
            ax.axhline(hi, color=color, linewidth=0.8, linestyle="--", alpha=0.7, zorder=2)
            ax.axhline(lo, color=color, linewidth=0.8, linestyle="--", alpha=0.7, zorder=2)
        else:
            ax.axhline(hi, color=color, linewidth=1.0, linestyle="-", alpha=0.8, zorder=2)

        # Label
        ax.annotate(
            ptype,
            xy=(len(df) - 0.5, hi),
            fontsize=7, color=color, alpha=0.9,
            ha="right", va="bottom",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SYNC RENDER  (runs in thread)
# ══════════════════════════════════════════════════════════════════════════════

def _render(df: pd.DataFrame, patterns_meta: list,
            symbol: str, timeframe: str) -> io.BytesIO:
    """
    Synchronous render — must be called via asyncio.to_thread.
    Returns PNG bytes in a BytesIO buffer.
    """
    title = f"{symbol}  ·  {timeframe}"
    fig, axlist = mpf.plot(
        df,
        type="candle",
        style=_DARK_STYLE,
        title=f"\n{title}",
        ylabel="",
        volume=True,
        volume_panel=1,
        panel_ratios=(4, 1),
        returnfig=True,
        figsize=(10, 6),
        tight_layout=True,
    )

    ax = axlist[0]
    _add_zones(ax, patterns_meta, df)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)   # release memory — clf() is NOT enough
    return buf


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

async def generate_chart(candles: list, patterns_meta: list,
                         symbol: str, timeframe: str) -> io.BytesIO | None:
    """
    Async entry point. Offloads matplotlib work to a thread.
    Returns BytesIO PNG or None on failure.
    patterns_meta: list of pattern dicts from scanner
                   (needs zone_high / zone_low / level fields for overlays)
    """
    if not candles:
        return None
    try:
        df  = candles_to_df(candles, timeframe)
        buf = await asyncio.to_thread(_render, df, patterns_meta, symbol, timeframe)
        return buf
    except Exception as e:
        logger.error(f"generate_chart {symbol} {timeframe}: {e}")
        return None
