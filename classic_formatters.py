"""Telegram message builders for the classic channel flow."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _season_emoji() -> str:
    month = datetime.now(timezone.utc).month
    if month in (9, 10, 11):
        return "🍂"
    if month in (12, 1, 2):
        return "❄️"
    return "🌤"


def _fmt_price(price: float) -> str:
    return f"{price:,.1f}" if price > 100 else f"{price:.4f}"


def _fmt_ts() -> str:
    return datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S")


def _ob_ticker(symbol: str) -> str:
    return "BTC.P" if "BTC" in symbol else "ETH.P"


def _ob_lines(orderbook: dict, symbol: str) -> list[str]:
    dominant = "more bids" if orderbook.get("dominant") == "bids" else "more asks"
    support = tuple(value or 0.0 for value in orderbook.get("support", (0.0, 0.0, 0.0)))
    resistance = tuple(value or 0.0 for value in orderbook.get("resistance", (0.0, 0.0, 0.0)))
    ticker = _ob_ticker(symbol)
    return [
        f"Order book: {dominant}",
        f"{_fmt_price(support[2])} {ticker} support: {_fmt_price(support[0])} - {_fmt_price(support[1])}",
        f"{_fmt_price(resistance[2])} {ticker} resistance: {_fmt_price(resistance[0])} - {_fmt_price(resistance[1])}",
    ]


def fmt_rsi(timeframe: str, label: str, symbols: list[str]) -> str:
    emoji = "🚨" if "Strongly" in label else "⚠️"
    tags = ", ".join(f"#{symbol}" for symbol in symbols)
    return f"{emoji} *{timeframe} {label}*\n{tags}\n_{_fmt_ts()}_"


def fmt_pattern(symbol: str, timeframe: str, pattern: str, direction: str, price: float, orderbook: dict) -> str:
    season = _season_emoji()
    pattern_emoji = "🔎" if pattern == "Predict" else "📍"
    direction_word = "up" if direction == "bullish" else "down"
    tag = f"#{symbol}.P"
    return "\n".join(
        [
            f"{season} *{timeframe} {pattern_emoji} {pattern}, possible reversal {direction_word} {tag} (BINANCE)*, price {_fmt_price(price)}",
            "",
            *_ob_lines(orderbook, symbol),
            f"_{_fmt_ts()}_",
        ]
    )


def fmt_setup(
    symbol: str,
    timeframe: str,
    trade_type: str,
    price: float,
    stop_loss: float,
    tp1: float,
    tp2: float,
    tp3: float,
    orderbook: dict,
) -> str:
    season = _season_emoji()
    is_long = "Long" in trade_type
    trade_emoji = "🎯" if "Scalp" in trade_type else ("📈" if is_long else "📉")
    tag = f"#{symbol}.P"
    close_dt = (datetime.now(timezone.utc) + timedelta(hours=20)).strftime("%d.%m.%Y %H:%M")
    return "\n".join(
        [
            f"{season} *{timeframe} {trade_emoji} {trade_type} {tag} (BINANCE)*, price {_fmt_price(price)}",
            "",
            f"Entry: {_fmt_price(price)}",
            f"Stop-loss: {_fmt_price(stop_loss)}",
            "",
            "Targets:",
            f"• 30% at {_fmt_price(tp1)}",
            f"• 30% at {_fmt_price(tp2)}",
            f"• 40% at {_fmt_price(tp3)}",
            f"• Close position in 20 hours (at {close_dt})",
            "",
            *_ob_lines(orderbook, symbol),
            f"_{_fmt_ts()}_",
        ]
    )


def fmt_bounce(symbol: str, timeframe: str, direction: str) -> str:
    season = _season_emoji()
    action = "bounce up" if direction == "bullish" else "pullback down"
    return f"{season} *{timeframe} ⚠️ Possible {action} #{symbol}.P*\n_{_fmt_ts()}_"


def fmt_cme(price: float) -> str:
    return f"⚠️ *CME (BTC1!) closed at {_fmt_price(price)}*\n_{_fmt_ts()}_"


__all__ = ["fmt_bounce", "fmt_cme", "fmt_pattern", "fmt_rsi", "fmt_setup"]
