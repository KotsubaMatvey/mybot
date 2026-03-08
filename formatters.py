"""
formatters.py — all message formatting functions
"""
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def score_label(score: int) -> str:
    stars  = "★" * score + "☆" * (5 - score)
    labels = {0: "", 1: "Weak", 2: "Moderate", 3: "Good", 4: "Strong", 5: "Excellent"}
    label  = labels.get(score, "")
    return f"{stars}  {label}".strip() if label else stars


def pattern_hint(ptype: str, direction: str) -> str:
    hints = {
        ("FVG",    "Bullish"):  "Unfilled gap below — potential support on retest",
        ("FVG",    "Bearish"):  "Unfilled gap above — potential resistance on retest",
        ("IFVG",   "Bullish"):  "Filled gap now acting as support",
        ("IFVG",   "Bearish"):  "Filled gap now acting as resistance",
        ("OB",     "Bullish"):  "Demand zone — last bearish candle before impulse",
        ("OB",     "Bearish"):  "Supply zone — last bullish candle before impulse",
        ("BOS",    "Bullish"):  "Structure broken upward — trend continuing",
        ("BOS",    "Bearish"):  "Structure broken downward — trend continuing",
        ("CHoCH",  "Bullish"):  "Character changed — possible reversal up",
        ("CHoCH",  "Bearish"):  "Character changed — possible reversal down",
        ("Swings", "High"):     "Swing high — liquidity pool above",
        ("Swings", "Low"):      "Swing low — liquidity pool below",
        ("Sweeps", "Bullish"):  "Liquidity swept below — watch for reversal",
        ("Sweeps", "Bearish"):  "Liquidity swept above — watch for reversal",
        ("Volume", "High"):     "Abnormal volume — institutional activity",
        ("PD",     "Premium"):  "Premium zone — favor sells",
        ("PD",     "Discount"): "Discount zone — favor buys",
    }
    return hints.get((ptype, direction), "")


def build_alert_message(symbol: str, timeframe: str, patterns_meta: list, score: int = 0) -> str:
    rating = score_label(score)
    lines  = [
        f"*{symbol}  ·  {timeframe}*",
        f"_{rating}_",
        "",
    ]
    for p in patterns_meta:
        detail = p.get("detail", "")
        hint   = pattern_hint(p.get("pattern", ""), p.get("direction", ""))
        lines.append(f"*{detail}*")
        if hint:
            lines.append(f"_{hint}_")
        lines.append("")
    lines.append(f"`{utc_now()}`")
    return "\n".join(lines)


def build_payment_message(price, expired: bool = False) -> str:
    expired_line = "\n⚠️ _Your subscription has expired._\n" if expired else ""
    return (
        f"💳 *Subscribe to ICT Crypto Alerts*\n"
        f"{expired_line}\n"
        f"*Price:*  `${price}` / month\n"
        f"_Pay in any crypto — USDT · TON · BTC · ETH_\n\n"
        f"*Includes:*\n"
        f"▪ Real-time ICT pattern alerts\n"
        f"▪ FVG · IFVG · OB · BOS · CHoCH · Swings\n"
        f"▪ Signal quality rating ★★★★★\n"
        f"▪ Market interpretations\n\n"
        f"_After payment tap_ ✅ *Check Payment* _below._"
    )


def build_dashboard_message(user: dict, zone_count: int, signals_today: int, sub_status: str) -> str:
    status   = "Active" if user["active"] else "Paused"
    conf     = "ON" if user.get("confluence", True) else "OFF"
    syms_str = "  ·  ".join(sorted(user["symbols"]))
    tfs_str  = "  ·  ".join(sorted(user["timeframes"]))
    return (
        f"📡 *ICT Crypto Alerts*\n\n"
        f"*Status:*  `{status}`\n"
        f"*Pairs:*  `{syms_str}`\n"
        f"*Timeframes:*  `{tfs_str}`\n"
        f"*Confluence:*  `{conf}`\n"
        f"*Subscription:*  {sub_status}\n\n"
        f"Last scan:  `{utc_now()}`\n"
        f"Active zones:  *{zone_count}*\n"
        f"Signals today:  *{signals_today}*"
    )


def build_setup_summary(symbols, patterns, timeframes) -> str:
    return (
        f"✅ *Setup Complete*\n\n"
        f"*Symbols*\n`{'  ·  '.join(sorted(symbols))}`\n\n"
        f"*Indicators*\n`{'  ·  '.join(sorted(patterns))}`\n\n"
        f"*Timeframes*\n`{'  ·  '.join(sorted(timeframes))}`\n\n"
        "_Alerts will arrive automatically._\n"
        "_Tap_ 📊 *Zones* _to see active setups now._"
    )
