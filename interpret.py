"""
Market interpretation module.
Converts detected ICT patterns into human-readable market context messages,
styled after professional trading channels.
"""

# ── RSI-like overbought/oversold via price position in range ──────────────────
def get_market_condition(candles: list) -> tuple[str, str]:
    """
    Returns (condition_label, direction) based on price position in recent range.
    Uses last 14 candles — analogous to RSI logic but price-based.
    """
    if len(candles) < 14:
        return "", ""
    lookback = candles[-14:]
    hi = max(c["high"] for c in lookback)
    lo = min(c["low"] for c in lookback)
    if hi == lo:
        return "", ""
    last_close = candles[-1]["close"]
    position = (last_close - lo) / (hi - lo)  # 0.0 = bottom, 1.0 = top

    if position >= 0.85:
        return "Сильно перекуплено", "bearish"
    elif position >= 0.65:
        return "Немного перекуплено", "bearish"
    elif position <= 0.15:
        return "Сильно перепродано", "bullish"
    elif position <= 0.35:
        return "Немного перепродано", "bullish"
    else:
        return "Нейтрально", "neutral"


def get_sl_tp(candles: list, direction: str) -> tuple[float, list]:
    """
    Calculate basic SL and 3 TP levels from recent swing structure.
    Returns (stop_loss, [tp1, tp2, tp3])
    """
    if len(candles) < 20:
        return 0.0, []
    lookback = candles[-20:]
    hi = max(c["high"] for c in lookback)
    lo = min(c["low"] for c in lookback)
    last = candles[-1]["close"]
    rng = hi - lo

    if direction == "bullish":
        sl   = round(lo - rng * 0.02, 4)
        tp1  = round(last + rng * 0.3, 4)
        tp2  = round(last + rng * 0.6, 4)
        tp3  = round(last + rng * 1.0, 4)
    else:
        sl   = round(hi + rng * 0.02, 4)
        tp1  = round(last - rng * 0.3, 4)
        tp2  = round(last - rng * 0.6, 4)
        tp3  = round(last - rng * 1.0, 4)
    return sl, [tp1, tp2, tp3]


def pattern_to_interpretation(patterns: list, candles: list, symbol: str, tf: str) -> str | None:
    """
    Given detected patterns and candles, produce a human-readable interpretation.
    Returns None if nothing significant to say.
    """
    if not patterns or not candles:
        return None

    last_price = candles[-1]["close"]
    pattern_types = {p["type"] for p in patterns}
    directions    = {p.get("direction", "") for p in patterns}

    # ── Determine main direction signal ──────────────────────────────────────
    bullish_score = sum([
        "Bullish" in directions,
        "BOS" in pattern_types and "Bullish" in directions,
        "CHoCH" in pattern_types and "Bullish" in directions,
        "Sweeps" in pattern_types and "Bullish" in directions,
        "IFVG" in pattern_types and "Bullish" in directions,
    ])
    bearish_score = sum([
        "Bearish" in directions,
        "BOS" in pattern_types and "Bearish" in directions,
        "CHoCH" in pattern_types and "Bearish" in directions,
        "Sweeps" in pattern_types and "Bearish" in directions,
        "IFVG" in pattern_types and "Bearish" in directions,
    ])

    condition, cond_dir = get_market_condition(candles)

    # Resolve direction
    if bullish_score > bearish_score:
        direction = "bullish"
    elif bearish_score > bullish_score:
        direction = "bearish"
    elif cond_dir in ("bullish", "bearish"):
        direction = cond_dir
    else:
        return None  # no clear signal

    dir_ru   = "Лонг" if direction == "bullish" else "Шорт"
    dir_sym  = "📈" if direction == "bullish" else "📉"

    # ── Select main pattern label ─────────────────────────────────────────────
    if "CHoCH" in pattern_types:
        signal_label = "⚡ CHoCH — возможен разворот"
        signal_type  = "reversal"
    elif "Sweeps" in pattern_types:
        signal_label = "↯ Свип ликвидности"
        signal_type  = "reversal"
    elif "BOS" in pattern_types:
        signal_label = "▲ BOS — пробой структуры"
        signal_type  = "trend"
    elif "IFVG" in pattern_types:
        signal_label = "◉ IFVG — возврат к зоне"
        signal_type  = "bounce"
    elif "FVG" in pattern_types:
        signal_label = "◈ FVG — незакрытый гэп"
        signal_type  = "bounce"
    elif "OB" in pattern_types:
        signal_label = "▣ OB — ордер блок"
        signal_type  = "bounce"
    elif condition and condition != "Нейтрально":
        signal_label = f"◌ {condition}"
        signal_type  = "condition"
    else:
        return None

    # ── Build scalp or trend message ──────────────────────────────────────────
    sl, tps = get_sl_tp(candles, direction)
    if not tps:
        return None

    # Signal type label
    if signal_type == "trend":
        trade_type = f"Трендовый {dir_ru}"
        emoji_trade = "↗️" if direction == "bullish" else "↘️"
    elif signal_type == "reversal":
        trade_type = f"Разворот {dir_ru}"
        emoji_trade = "🔄"
    else:
        trade_type = f"Скальп {dir_ru}"
        emoji_trade = "⚡"

    # Condition label
    cond_line = f"_{condition}_\n" if condition and condition != "Нейтрально" else ""

    # Format price
    def fmt(p):
        return f"{p:,.2f}" if p > 100 else f"{p:.4f}"

    lines = [
        f"🍀 *{tf}  {emoji_trade}  {trade_type}*",
        f"*#{symbol}*  ·  текущая цена `{fmt(last_price)}`",
        "",
    ]
    if cond_line:
        lines.append(cond_line)

    lines += [
        f"*{signal_label}*",
        "",
        f"Вход: `{fmt(last_price)}`",
        f"Стоп-лосс: `{fmt(sl)}`",
        "",
        "Цели:",
        f"▪ 30% на `{fmt(tps[0])}`",
        f"▪ 30% на `{fmt(tps[1])}`",
        f"▪ 40% на `{fmt(tps[2])}`",
    ]

    return "\n".join(lines)
