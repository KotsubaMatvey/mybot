from __future__ import annotations

import logging

import payment_flow
from database import get_user
from formatters import build_alert_message
from scanner import get_cached_candles, get_cached_patterns
from visuals import generate_chart

from .common import filter_cached_alerts

logger = logging.getLogger(__name__)


async def charts_cmd(update, context):
    from database import toggle_charts

    user_id = update.effective_user.id
    if not payment_flow.is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    new_state = toggle_charts(user_id)
    state_text = "ON" if new_state else "OFF"
    hint = "Chart sent with every alert" if new_state else "Tap Chart under any alert to view"
    await update.message.reply_text(f"Auto Charts: {state_text}\n\n{hint}")


async def chart_cmd(update, context):
    user_id = update.effective_user.id
    if not payment_flow.is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /chart BTCUSDT 1h")
        return

    symbol = context.args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    timeframe = context.args[1].lower()
    await _send_chart_reply(update.message, user_id, symbol, timeframe)


async def handle_chart_callback(update, context):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        await query.message.reply_text("Invalid chart request.")
        return
    _, symbol, timeframe = parts

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    await _send_chart_reply(query.message, query.from_user.id, symbol, timeframe)


async def _send_chart_reply(target_message, user_id: int, symbol: str, timeframe: str) -> None:
    candles = get_cached_candles(symbol, timeframe)
    if not candles:
        await target_message.reply_text(f"No data for {symbol} {timeframe} yet. Wait for the next scan.")
        return

    loading = await target_message.reply_text("Generating chart...")
    try:
        user = get_user(user_id)
        patterns = filter_cached_alerts(get_cached_patterns(symbol, timeframe), user)
        chart = await generate_chart(candles, patterns, symbol, timeframe)
        if chart is None:
            await loading.edit_text("Chart generation failed.")
            return
        await loading.delete()
        caption = build_alert_message(symbol, timeframe, patterns) if patterns else f"{symbol}  {timeframe}"
        await target_message.reply_photo(photo=chart, caption=caption)
    except Exception as exc:
        logger.error("chart %s %s: %s", symbol, timeframe, exc)
        await loading.edit_text("Error generating chart.")


__all__ = ["chart_cmd", "charts_cmd", "handle_chart_callback"]
