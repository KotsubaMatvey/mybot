"""
classic_formatters.py — message builders for the Telegram channel.
Replicates Better Trader Insights format exactly.
Pure functions — no I/O.
"""
from datetime import datetime, timezone, timedelta


def _season_emoji() -> str:
    m = datetime.now(timezone.utc).month
    return "🍂" if m in (9, 10, 11) else "❄️" if m in (12, 1, 2) else "🍀"


def _fmt_price(p: float) -> str:
    return f"{p:,.1f}" if p > 100 else f"{p:.4f}"


def _fmt_ts() -> str:
    return datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S")


def _ob_ticker(symbol: str) -> str:
    return "BTC.P" if "BTC" in symbol else "ETH.P"


def _ob_lines(ob: dict, symbol: str) -> list[str]:
    """Shared orderbook block used in Type 2 and Type 3 messages."""
    dom = "📗 more bids" if ob.get("dominant") == "bids" else "📕 more asks"
    sup = ob.get("support",    (0.0, 0.0, 0.0))
    res = ob.get("resistance", (0.0, 0.0, 0.0))
    sup = tuple(v or 0.0 for v in sup)
    res = tuple(v or 0.0 for v in res)
    tk  = _ob_ticker(symbol)
    return [
        f"Order book: {dom}",
        f"{_fmt_price(sup[2])} {tk} support: {_fmt_price(sup[0])} - {_fmt_price(sup[1])}",
        f"{_fmt_price(res[2])} {tk} resistance: {_fmt_price(res[0])} - {_fmt_price(res[1])}",
    ]


# ── Type 1: RSI alert ─────────────────────────────────────────────────────────

def fmt_rsi(tf: str, label: str, symbols: list[str]) -> str:
    """
    ⚠️ 1H Strongly oversold
    #BTCUSDT, #ETHUSDT
    17-Oct-2025 10:01:01
    """
    emoji = "⚠️" if "Strongly" in label else "☀️"
    tags  = ", ".join(f"#{s}" for s in symbols)
    return f"{emoji} *{tf} {label}*\n{tags}\n_{_fmt_ts()}_"


# ── Type 2: Pattern with OB ───────────────────────────────────────────────────

def fmt_pattern(symbol: str, tf: str, pattern: str, direction: str,
                price: float, ob: dict) -> str:
    """
    🍀 30M 👁 Predict, possible reversal up #BTCUSDT.P (BINANCE), price 105132.1

    Order book: 📗 more bids
    179 BTC.P support: 104080.8 - 105132.1
    17-Oct-2025 11:30:02
    """
    se       = _season_emoji()
    p_emoji  = "👁" if pattern == "Predict" else "🔪"
    dir_word = "up" if direction == "bullish" else "down"
    tag      = f"#{symbol}.P"

    return "\n".join([
        f"{se} *{tf} {p_emoji} {pattern}, possible reversal {dir_word} {tag} (BINANCE)*, price {_fmt_price(price)}",
        "",
        *_ob_lines(ob, symbol),
        f"_{_fmt_ts()}_",
    ])


# ── Type 3: Full setup ────────────────────────────────────────────────────────

def fmt_setup(symbol: str, tf: str, trade_type: str, price: float,
              sl: float, tp1: float, tp2: float, tp3: float, ob: dict) -> str:
    """
    🍀 4H ⚡ Scalp Long #BTCUSDT.P (BINANCE), price 113355.2

    Entry: 113355.2 / Stop-loss: 110180
    Targets: 30% at ... / Close position in 20 hours
    Order book: ...
    """
    se       = _season_emoji()
    is_long  = "Long" in trade_type
    t_emoji  = "⚡" if "Scalp" in trade_type else ("↗️" if is_long else "↘️")
    tag      = f"#{symbol}.P"
    close_dt = (datetime.now(timezone.utc) + timedelta(hours=20)).strftime("%d.%m.%Y %H:%M")

    return "\n".join([
        f"{se} *{tf} {t_emoji} {trade_type} {tag} (BINANCE)*, price {_fmt_price(price)}",
        "",
        f"Entry: {_fmt_price(price)}",
        f"Stop-loss: {_fmt_price(sl)}",
        "",
        "Targets:",
        f"▪️ 30% at {_fmt_price(tp1)}",
        f"▪️ 30% at {_fmt_price(tp2)}",
        f"▪️ 40% at {_fmt_price(tp3)}",
        f"▪️ Close position in 20 hours (at {close_dt})",
        "",
        *_ob_lines(ob, symbol),
        f"_{_fmt_ts()}_",
    ])


# ── Type 4: Bounce ────────────────────────────────────────────────────────────

def fmt_bounce(symbol: str, tf: str, direction: str) -> str:
    """🍀 1H ☀️ Possible bounce up #BTCUSDT.P"""
    se     = _season_emoji()
    action = "bounce up" if direction == "bullish" else "pullback down"
    return f"{se} *{tf} ☀️ Possible {action} #{symbol}.P*\n_{_fmt_ts()}_"


# ── Type 5: CME close ─────────────────────────────────────────────────────────

def fmt_cme(price: float) -> str:
    return f"☀️ *CME (BTC1!) closed at {_fmt_price(price)}*\n_{_fmt_ts()}_"
