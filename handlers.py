"""
handlers.py — command handlers and top-level routing only.
Business logic lives in: onboarding.py, payment_flow.py, formatters.py
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_user, upsert_user, set_active,
    is_subscribed, get_subscription_status, set_owner,
    toggle_sessions_alerts, toggle_charts
)
from scanner import get_active_zones
from keyboards import main_menu, confirm_stop_keyboard
from formatters import build_dashboard_message, build_alert_message, utc_now
from alerts import signals_today
from config import SYMBOLS, TIMEFRAMES, OWNER_IDS, WELCOME_PHOTO
from sessions import get_current_session_message
from visuals  import generate_chart
from scanner  import get_cached_candles, get_cached_patterns
import onboarding
import payment_flow

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

async def send_dashboard(user_id: int, context, update=None):
    user       = get_user(user_id)
    zones      = get_active_zones()
    today      = signals_today.get(user_id, 0)
    sub_status = get_subscription_status(user_id)

    zone_count = sum(
        1 for sym in user["symbols"]
        for tf, patterns in zones.get(sym, {}).items()
        if tf in user["timeframes"]
        for p in patterns if p["type"] in user["patterns"]
    )
    text = build_dashboard_message(user, zone_count, today, sub_status)
    if update:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await context.bot.send_message(user_id, text, reply_markup=main_menu())


# ══════════════════════════════════════════════════════════════════════════════
#  COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    if user_id in OWNER_IDS:
        set_owner(user_id)
    user = get_user(user_id)

    if user and user["setup_done"] and is_subscribed(user_id):
        await send_dashboard(user_id, context, update)
        return
    if user and user["setup_done"] and not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return

    photo_path = WELCOME_PHOTO
    welcome_text = (
        "📡 ICT Crypto Alerts\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "Patterns:\n"
        "FVG | IFVG | OB | BOS | CHoCH\n"
        "Swings | Sweeps | Volume\n\n"
        "Market analysis tool. Not financial advice."
    )
    try:
        with open(photo_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
            )
    except Exception:
        await update.message.reply_text(welcome_text)
    await payment_flow.send_payment_screen(user_id, context, update)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    onboarding.init(user_id)
    await update.message.reply_text(
        "⚙️ *Reset Preferences*\n\n_Setting up from scratch._",
        parse_mode="Markdown"
    )
    await onboarding.send_step_symbols(user_id, context)


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏸ *Pause Alerts*\n\nAre you sure?",
        parse_mode="Markdown",
        reply_markup=confirm_stop_keyboard()
    )


async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user or not user["setup_done"]:
        await update.message.reply_text("No subscription found. Send /start")
        return
    set_active(update.effective_user.id, True)
    await update.message.reply_text(
        "▶️ *Alerts Resumed*\n\n_You will now receive alerts._",
        parse_mode="Markdown"
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user    = get_user(user_id)
    if not user or not user["setup_done"]:
        await update.message.reply_text("No active subscription. Send /start")
        return
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return
    await send_dashboard(user_id, context, update)


async def zones_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user or not user["setup_done"]:
        await update.message.reply_text("Send /start first.")
        return

    zones = get_active_zones()
    lines = ["📊 *Active ICT Zones*"]
    has   = False

    for symbol in sorted(user["symbols"]):
        sym_lines = [f"\n*{symbol}*"]
        for tf in TIMEFRAMES:
            if tf not in user["timeframes"]:
                continue
            for p in zones.get(symbol, {}).get(tf, []):
                if p["type"] not in user["patterns"]:
                    continue
                sym_lines.append(f"  `{tf}`  {p['detail']}")
                has = True
        if len(sym_lines) > 1:
            lines.extend(sym_lines)

    if not has:
        await update.message.reply_text(
            "📊 *Active ICT Zones*\n\n_No active zones. Scans run every 60s._",
            parse_mode="Markdown"
        )
        return
    lines += ["", f"_Updated: {utc_now()}_"]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")




async def sessions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle session alerts + show current session."""
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return

    # If called from menu button — toggle and confirm
    new_state = toggle_sessions_alerts(user_id)
    state_str = "ON 🟢" if new_state else "OFF 🔴"

    current = await get_current_session_message()

    await update.message.reply_text(
        f"🕐 *Session Alerts:*  `{state_str}`\n\n{current}",
        parse_mode="Markdown"
    )


async def session_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/session — show current session without toggling."""
    current = await get_current_session_message()
    await update.message.reply_text(current, parse_mode="Markdown")


async def charts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle auto chart generation via menu button."""
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    new_state = toggle_charts(user_id)
    state_str = "ON 🟢" if new_state else "OFF 🔴"
    hint = "Chart sent with every alert" if new_state else "Tap 📈 Chart under any alert to view"
    await update.message.reply_text(
        f"📈 *Auto Charts:*  `{state_str}`\n\n_{hint}_",
        parse_mode="Markdown",
    )


async def chart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/chart BTCUSDT 1h — generate chart on demand."""
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Usage: `/chart BTCUSDT 1h`", parse_mode="Markdown")
        return

    symbol  = args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    tf      = args[1].lower()
    candles = get_cached_candles(symbol, tf)

    if not candles:
        await update.message.reply_text(
            f"No data for `{symbol} {tf}` yet — wait for the next scan.",
            parse_mode="Markdown",
        )
        return

    msg = await update.message.reply_text("⏳ Generating chart…")
    try:
        user     = get_user(user_id)
        u_pats   = set(user.get("patterns", []))
        patterns = get_cached_patterns(symbol, tf)
        patterns = [p for p in patterns if p.get("pattern") in u_pats]
        chart = await generate_chart(candles, patterns, symbol, tf)
        if not chart:
            await msg.edit_text("Chart generation failed.")
            return
        await msg.delete()
        caption = build_alert_message(symbol, tf, patterns) if patterns else f"{symbol}  ·  {tf}"
        await update.message.reply_photo(photo=chart, caption=caption)
    except Exception as e:
        logger.error(f"chart_cmd {symbol} {tf}: {e}")
        await msg.edit_text("Error generating chart.")


async def handle_chart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles 📈 Chart inline button under alerts."""
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
        await query.message.reply_text(
            f"No cached data for `{symbol} {tf}` — wait for next scan.",
            parse_mode="Markdown",
        )
        return

    loading = await query.message.reply_text("⏳ Generating chart…")
    try:
        user     = get_user(query.from_user.id)
        u_pats   = set(user.get("patterns", []))
        patterns = get_cached_patterns(symbol, tf)
        patterns = [p for p in patterns if p.get("pattern") in u_pats]
        chart = await generate_chart(candles, patterns, symbol, tf)
        if not chart:
            await loading.edit_text("Chart generation failed.")
            return
        await loading.delete()
        caption = build_alert_message(symbol, tf, patterns) if patterns else f"{symbol}  ·  {tf}"
        await query.message.reply_photo(photo=chart, caption=caption)
    except Exception as e:
        logger.error(f"chart callback {symbol} {tf}: {e}")
        await loading.edit_text("Error generating chart.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *ICT Crypto Alerts — Help*\n\n"
        "*Commands*\n"
        "`/start`       Dashboard or setup\n"
        "`/pay`         Subscription & payment\n"
        "`/zones`       Active zones now\n"
        "`/status`      Subscription overview\n"
        "`/reset`       Change preferences\n"
        "`/stop`        Pause alerts\n"
        "`/resume`      Resume alerts\n"
        "`/session`     Current session\n\n"
        "*Patterns*\n"
        "`FVG`  `IFVG`  `OB`  `BOS`  `CHoCH`\n"
        "`Swings`  `Sweeps`  `Volume`  `PD`\n\n"
        "⚠️ _Not financial advice._",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CALLBACK ROUTER — delegates to sub-modules
# ══════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data    = query.data

    # Stop/resume confirmation
    if data == "stop_confirm":
        set_active(user_id, False)
        await query.edit_message_text(
            "⏸ *Alerts Paused*\n\n_Tap ▶️ Resume to restart._",
            parse_mode="Markdown"
        )
        return
    if data == "stop_cancel":
        await query.edit_message_text(
            "*Cancelled*\n\n_Alerts remain active._",
            parse_mode="Markdown"
        )
        return

    # Chart button
    if data.startswith("chart_"):
        await handle_chart_callback(update, context)
        return

    # Delegate to payment flow
    if await payment_flow.handle_callback(user_id, data, query, context):
        return

    # Delegate to onboarding
    if await onboarding.handle_callback(user_id, data, query, context):
        return

    await query.edit_message_text("Session expired. Tap /start")


# ══════════════════════════════════════════════════════════════════════════════
#  MENU BUTTON ROUTER
# ══════════════════════════════════════════════════════════════════════════════

async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        await update.message.delete()
    except Exception:
        pass

    dispatch = {
        "▦ ZONES":     zones_cmd,
        "◎ SETTINGS":  reset,
        "◈ STATUS":    status_cmd,
        "? HELP":      help_cmd,
        "■ STOP":      stop_cmd,
        "▶ RESUME":    resume_cmd,
        "◷ SESSIONS":  sessions_cmd,
        "▤ CHARTS":    charts_cmd,
    }
    handler = dispatch.get(text)
    if handler:
        await handler(update, context)
