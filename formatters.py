"""
formatters.py — all message formatting functions
"""
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def fmt_price(p: float) -> str:
    """
    Adaptive price formatting:
      >= 1000  → 1 decimal  (66445.1)
      >= 1     → 2 decimals (1.85)
      < 1      → 4 decimals (0.0023)
    """
    if p >= 1000:
        return f"{p:,.1f}"
    if p >= 1:
        return f"{p:.2f}"
    return f"{p:.4f}"




def build_alert_message(symbol: str, timeframe: str, patterns_meta: list) -> str:
    lines = [f"{symbol}  ·  {timeframe}"]
    for p in patterns_meta:
        detail = p.get("detail", "")
        lines.append(f"■  {detail}")
    return "\n".join(lines)


def build_payment_message(price, expired: bool = False) -> str:
    expired_line = "\n⚠️ _Your subscription has expired._\n" if expired else ""
    return (
        f"💳 *Subscribe to ICT Crypto Alerts*\n"
        f"{expired_line}\n"
        f"*Price:*  `${price}` / month\n"
        f"_Pay in any crypto — USDT · TON · BTC · ETH_\n\n"
        f"*Includes:*\n"
        f"▪ Real-time ICT pattern detection\n"
        f"▪ FVG · IFVG · OB · BOS · CHoCH · Swings\n"
        f"▪ Multi-timeframe zone tracking\n"
        f"_After payment tap_ ✅ *Check Payment* _below._"
    )


def build_dashboard_message(user: dict, zone_count: int, alerts_today: int, sub_status: str) -> str:
    status   = "Active" if user["active"] else "Paused"
    syms_str = " | ".join(sorted(user["symbols"]))
    tfs_str  = " | ".join(sorted(user["timeframes"]))
    return (
        f"📡 ICT Crypto Alerts\n\n"
        f"Status: {status}\n"
        f"Pairs: {syms_str}\n"
        f"Timeframes: {tfs_str}\n"
        f"Subscription: {sub_status}\n\n"
        f"Last scan: {utc_now()}\n"
        f"Active zones: {zone_count}\n"
        f"Alerts today: {alerts_today}"
    )


def build_setup_summary(symbols, patterns, timeframes) -> str:
    syms = ", ".join(sorted(symbols))
    pats = ", ".join(sorted(patterns))
    tfs  = ", ".join(sorted(timeframes))
    return (
        f"Preferences set! You have chosen: {syms} — {pats} — {tfs}\n\n"
        f"_Alerts will arrive automatically._"
    )
