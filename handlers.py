"""
handlers.py — command handlers and top-level routing only.
Business logic lives in: onboarding.py, payment_flow.py, formatters.py
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_user, upsert_user, set_active,
    is_subscribed, get_subscription_status, set_owner
)
from scanner import get_active_zones
from keyboards import main_menu, confirm_stop_keyboard
from formatters import build_dashboard_message, utc_now
from alerts import signals_today
from config import SYMBOLS, TIMEFRAMES, OWNER_IDS
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
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu())
    else:
        await context.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=main_menu())


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

    await update.message.reply_text(
        "👋 *Welcome to ICT Crypto Alerts*\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "*Patterns:*\n"
        "`FVG · IFVG · OB · BOS · CHoCH`\n"
        "`Swings · Sweeps · Volume · PD`\n\n"
        "*Signal rating:*  ★☆☆☆☆ — ★★★★★\n\n"
        "⚠️ _Market analysis tool. Not financial advice._",
        parse_mode="Markdown"
    )
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


async def confluence_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user    = get_user(user_id)
    if not user or not user["setup_done"]:
        await update.message.reply_text("Send /start first.")
        return
    new_val = not user.get("confluence", True)
    upsert_user(user_id, confluence=int(new_val))
    state = "ON" if new_val else "OFF"
    await update.message.reply_text(
        f"🔥 *Market Interpretations:*  `{state}`",
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *ICT Crypto Alerts — Help*\n\n"
        "*Commands*\n"
        "`/start`       Dashboard or setup\n"
        "`/pay`         Subscription & payment\n"
        "`/zones`       Active zones now\n"
        "`/status`      Subscription overview\n"
        "`/reset`       Change preferences\n"
        "`/confluence`  Toggle interpretations\n"
        "`/stop`        Pause alerts\n"
        "`/resume`      Resume alerts\n\n"
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
        "📊 Zones":      zones_cmd,
        "⚙️ Settings":  reset,
        "ℹ️ Status":    status_cmd,
        "❓ Help":       help_cmd,
        "⏸ Stop":       stop_cmd,
        "▶️ Resume":    resume_cmd,
        "🔥 Confluence": confluence_cmd,
    }
    handler = dispatch.get(text)
    if handler:
        await handler(update, context)
