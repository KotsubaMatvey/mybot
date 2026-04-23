"""Telegram handlers and top-level routing."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

import onboarding
import payment_flow
from alerts import signals_today
from config import OWNER_IDS, TIMEFRAMES, WELCOME_PHOTO
from database import (
    get_subscription_status,
    get_user,
    is_subscribed,
    set_active,
    set_owner,
    toggle_charts,
    toggle_sessions_alerts,
    upsert_user,
)
from formatters import build_alert_message, build_dashboard_message, utc_now
from keyboards import confirm_stop_keyboard, main_menu
from scanner import get_active_zones, get_cached_candles, get_cached_patterns
from sessions import get_current_session_message
from visuals import generate_chart

logger = logging.getLogger(__name__)


def _user_ready(user: dict | None) -> bool:
    if not user:
        return False
    return bool(
        user.get("setup_done")
        and user.get("symbols")
        and user.get("patterns")
        and user.get("timeframes")
        and user.get("entry_models")
        and user.get("trade_directions")
    )


def _alert_enabled_for_user(alert: dict, user: dict) -> bool:
    if alert.get("alert_kind") == "strategy":
        setup = alert.get("setup")
        direction = getattr(setup, "direction", None) if setup else None
        return (
            alert.get("pattern") in user.get("entry_models", set())
            and direction in user.get("trade_directions", set())
        )
    return alert.get("pattern") in user.get("patterns", set())


def _filter_cached_alerts(patterns: list[dict], user: dict | None) -> list[dict]:
    if not user:
        return []
    return [pattern for pattern in patterns if _alert_enabled_for_user(pattern, user)]


async def send_dashboard(user_id: int, context, update=None):
    user = get_user(user_id)
    zones = get_active_zones()
    today = signals_today.get(user_id, 0)
    sub_status = get_subscription_status(user_id)

    zone_count = sum(
        1
        for symbol in user["symbols"]
        for tf, patterns in zones.get(symbol, {}).items()
        if tf in user["timeframes"]
        for pattern in patterns
        if _alert_enabled_for_user(pattern, user)
    )
    text = build_dashboard_message(user, zone_count, today, sub_status)
    if update:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await context.bot.send_message(user_id, text, reply_markup=main_menu())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    if user_id in OWNER_IDS:
        set_owner(user_id)
    user = get_user(user_id)

    if _user_ready(user):
        if is_subscribed(user_id):
            await send_dashboard(user_id, context, update)
            return
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return

    if user_id in OWNER_IDS or is_subscribed(user_id):
        onboarding.init(user_id)
        await update.message.reply_text(
            "Setup Preferences\n\nSelect symbols, primitive alerts, timeframes, entry models and directions.",
        )
        await onboarding.send_step_symbols(user_id, context)
        return

    welcome_text = (
        "ICT Crypto Alerts\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "Primitives:\n"
        "FVG | IFVG | OB | BOS | CHoCH | Sweeps | Liquidity\n\n"
        "Strategies:\n"
        "Entry Model 1 | Entry Model 2 | Entry Model 3\n\n"
        "Market analysis tool. Not financial advice."
    )
    try:
        with open(WELCOME_PHOTO, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=welcome_text)
    except Exception:
        await update.message.reply_text(welcome_text)
    await payment_flow.send_payment_screen(user_id, context, update)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    onboarding.init(user_id)
    await update.message.reply_text("Reset Preferences\n\nSetting up from scratch.")
    await onboarding.send_step_symbols(user_id, context)


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pause Alerts\n\nAre you sure?", reply_markup=confirm_stop_keyboard())


async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not _user_ready(user):
        if is_subscribed(update.effective_user.id):
            await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        else:
            await update.message.reply_text("No subscription found. Send /start")
        return
    set_active(update.effective_user.id, True)
    await update.message.reply_text("Alerts resumed.\n\nYou will now receive alerts.")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not _user_ready(user):
        if is_subscribed(user_id):
            await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        else:
            await update.message.reply_text("No active subscription. Send /start")
        return
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return
    await send_dashboard(user_id, context, update)


async def zones_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return
    user = get_user(user_id)
    if not _user_ready(user):
        await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        return

    zones = get_active_zones()
    lines = ["Active ICT Zones"]
    has = False

    for symbol in sorted(user["symbols"]):
        symbol_lines = [f"\n{symbol}"]
        for tf in TIMEFRAMES:
            if tf not in user["timeframes"]:
                continue
            for pattern in zones.get(symbol, {}).get(tf, []):
                if not _alert_enabled_for_user(pattern, user):
                    continue
                symbol_lines.append(f"  {tf}  {pattern['detail']}")
                has = True
        if len(symbol_lines) > 1:
            lines.extend(symbol_lines)

    if not has:
        await update.message.reply_text("Active ICT Zones\n\nNo active zones. Scans run every 60s.")
        return
    lines += ["", f"Updated: {utc_now()}"]
    await update.message.reply_text("\n".join(lines))


async def sessions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    new_state = toggle_sessions_alerts(user_id)
    state_str = "ON" if new_state else "OFF"
    current = await get_current_session_message()
    await update.message.reply_text(f"Session Alerts: {state_str}\n\n{current}")


async def session_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await get_current_session_message()
    await update.message.reply_text(current)


async def charts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    new_state = toggle_charts(user_id)
    state_str = "ON" if new_state else "OFF"
    hint = "Chart sent with every alert" if new_state else "Tap Chart under any alert to view"
    await update.message.reply_text(f"Auto Charts: {state_str}\n\n{hint}")


async def chart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /chart BTCUSDT 1h")
        return

    symbol = context.args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    tf = context.args[1].lower()
    candles = get_cached_candles(symbol, tf)
    if not candles:
        await update.message.reply_text(f"No data for {symbol} {tf} yet - wait for the next scan.")
        return

    msg = await update.message.reply_text("Generating chart...")
    try:
        user = get_user(user_id)
        patterns = _filter_cached_alerts(get_cached_patterns(symbol, tf), user)
        chart = await generate_chart(candles, patterns, symbol, tf)
        if not chart:
            await msg.edit_text("Chart generation failed.")
            return
        await msg.delete()
        caption = build_alert_message(symbol, tf, patterns) if patterns else f"{symbol}  ·  {tf}"
        await update.message.reply_photo(photo=chart, caption=caption)
    except Exception as exc:
        logger.error("chart_cmd %s %s: %s", symbol, tf, exc)
        await msg.edit_text("Error generating chart.")


async def handle_chart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        return
    _, symbol, tf = parts

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    candles = get_cached_candles(symbol, tf)
    if not candles:
        await query.message.reply_text(f"No cached data for {symbol} {tf} - wait for next scan.")
        return

    loading = await query.message.reply_text("Generating chart...")
    try:
        user = get_user(query.from_user.id)
        patterns = _filter_cached_alerts(get_cached_patterns(symbol, tf), user)
        chart = await generate_chart(candles, patterns, symbol, tf)
        if not chart:
            await loading.edit_text("Chart generation failed.")
            return
        await loading.delete()
        caption = build_alert_message(symbol, tf, patterns) if patterns else f"{symbol}  ·  {tf}"
        await query.message.reply_photo(photo=chart, caption=caption)
    except Exception as exc:
        logger.error("chart callback %s %s: %s", symbol, tf, exc)
        await loading.edit_text("Error generating chart.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ICT Crypto Alerts - Help\n\n"
        "Commands\n"
        "/start       Dashboard or setup\n"
        "/pay         Subscription and payment\n"
        "/zones       Active zones now\n"
        "/status      Subscription overview\n"
        "/reset       Change preferences\n"
        "/stop        Pause alerts\n"
        "/resume      Resume alerts\n"
        "/session     Current session\n"
        "/chart       Render a chart from cache\n\n"
        "Primitive alerts\n"
        "FVG  IFVG  OB  BOS  CHoCH  Sweeps  Liquidity  Breaker\n"
        "Swings  Volume  VP  KL  PD  EQH  EQL  SMT\n\n"
        "Entry models\n"
        "Entry Model 1  Entry Model 2  Entry Model 3\n\n"
        "Not financial advice."
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "stop_confirm":
        await query.answer()
        set_active(user_id, False)
        await query.edit_message_text("Alerts paused.\n\nTap Resume to restart.")
        return
    if data == "stop_cancel":
        await query.answer()
        await query.edit_message_text("Cancelled.\n\nAlerts remain active.")
        return
    if data.startswith("chart_"):
        await handle_chart_callback(update, context)
        return
    if await payment_flow.handle_callback(user_id, data, query, context):
        return
    if await onboarding.handle_callback(user_id, data, query, context):
        return
    await query.answer()
    await query.edit_message_text("Session expired. Tap /start")


async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        await update.message.delete()
    except Exception:
        pass

    dispatch = {
        "ZONES": zones_cmd,
        "SETTINGS": reset,
        "STATUS": status_cmd,
        "HELP": help_cmd,
        "STOP": stop_cmd,
        "RESUME": resume_cmd,
        "SESSIONS": sessions_cmd,
        "CHARTS": charts_cmd,
        "▪ ZONES": zones_cmd,
        "◉ SETTINGS": reset,
        "◎ STATUS": status_cmd,
        "? HELP": help_cmd,
        "■ STOP": stop_cmd,
        "▶ RESUME": resume_cmd,
        "◷ SESSIONS": sessions_cmd,
        "▤ CHARTS": charts_cmd,
    }
    handler = dispatch.get(text)
    if handler:
        await handler(update, context)
