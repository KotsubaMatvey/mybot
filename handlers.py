"""
handlers.py — all Telegram command and callback handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, Application

from database import (
    get_user, upsert_user, get_all_active_users,
    save_preferences, set_active,
    is_subscribed, set_subscription, get_subscription_status, set_owner
)
from payments import create_invoice, check_invoice, SUBSCRIPTION_PRICE
from scanner import get_active_zones, ALL_PATTERNS
from keyboards import (
    main_menu, build_toggle_keyboard, confirm_stop_keyboard, payment_keyboard
)
from formatters import (
    build_alert_message, build_payment_message, build_dashboard_message,
    build_setup_summary, utc_now
)
from alerts import signals_today
from config import SYMBOLS, TIMEFRAMES, OWNER_IDS

logger = logging.getLogger(__name__)

# Onboarding state — {user_id: {symbols, patterns, timeframes}}
onboarding: dict = {}
# Pending payments — {user_id: invoice_id}
pending_payments: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  ONBOARDING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def init_onboarding(user_id: int):
    onboarding[user_id] = {"symbols": set(), "patterns": set(), "timeframes": set()}


async def send_symbol_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("symbols", set())
    kb   = build_toggle_keyboard(SYMBOLS, sel, "sym")
    text = "*Step 1 of 3 — Symbols*\n\nSelect the pairs you want to track:"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)


async def send_indicator_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("patterns", set())
    kb   = build_toggle_keyboard(ALL_PATTERNS, sel, "pat")
    text = "*Step 2 of 3 — Indicators*\n\nSelect which patterns to detect:"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)


async def send_timeframe_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("timeframes", set())
    kb   = build_toggle_keyboard(TIMEFRAMES, sel, "tf")
    text = "*Step 3 of 3 — Timeframes*\n\nSelect timeframes:\n_Tip: 15m + 1h + 4h covers most ICT setups_"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)


# ══════════════════════════════════════════════════════════════════════════════
#  PAYMENT HELPER
# ══════════════════════════════════════════════════════════════════════════════

async def send_payment_screen(user_id, context, update=None, expired=False):
    inv = await create_invoice(user_id)
    if not inv:
        text = "❌ *Payment system unavailable*\n\n_Please try again later._"
        if update:
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await context.bot.send_message(user_id, text, parse_mode="Markdown")
        return

    pending_payments[user_id] = inv["invoice_id"]
    upsert_user(user_id, invoice_id=inv["invoice_id"])

    text = build_payment_message(SUBSCRIPTION_PRICE, expired)
    kb   = payment_keyboard(inv["pay_url"], inv["invoice_id"], SUBSCRIPTION_PRICE)

    if update:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=kb)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD HELPER
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
        await send_payment_screen(user_id, context, update, expired=True)
        return

    welcome = (
        "👋 *Welcome to ICT Crypto Alerts*\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "*Patterns:*\n"
        "`FVG · IFVG · OB · BOS · CHoCH`\n"
        "`Swings · Sweeps · Volume · PD`\n\n"
        "*Signal rating:*  ★☆☆☆☆ — ★★★★★\n\n"
        "⚠️ _Market analysis tool. Not financial advice._"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")
    await send_payment_screen(user_id, context, update)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await send_payment_screen(user_id, context, update)
        return
    init_onboarding(user_id)
    await update.message.reply_text(
        "⚙️ *Reset Preferences*\n\n_Setting up from scratch._",
        parse_mode="Markdown"
    )
    await send_symbol_step(user_id, context)


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
        await send_payment_screen(user_id, context, update, expired=True)
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


async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    upsert_user(user_id)
    if is_subscribed(user_id):
        status = get_subscription_status(user_id)
        await update.message.reply_text(
            f"💳 *Subscription*\n\n{status}",
            parse_mode="Markdown"
        )
        return
    await send_payment_screen(user_id, context, update)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
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
        "⚠️ _Not financial advice._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data    = query.data

    # Payment check
    if data.startswith("check_pay_"):
        invoice_id = int(data.split("_")[2])
        paid = await check_invoice(invoice_id)
        if paid:
            set_subscription(user_id, 30)
            pending_payments.pop(user_id, None)
            await query.edit_message_text(
                "✅ *Payment confirmed!*\n\n_Your 30-day subscription is now active._",
                parse_mode="Markdown"
            )
            init_onboarding(user_id)
            await context.bot.send_message(
                user_id, "Let's set up your preferences:",
                reply_markup=main_menu()
            )
            await send_symbol_step(user_id, context)
        else:
            await query.answer("Payment not found yet. Please complete payment and try again.", show_alert=True)
        return

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

    # Onboarding
    if user_id not in onboarding:
        await query.edit_message_text("Session expired. Tap /start")
        return

    ob = onboarding[user_id]

    if data.startswith("sym_"):
        item = data[4:]
        if item == "CONFIRM":
            if not ob["symbols"]:
                await query.answer("Select at least one symbol!", show_alert=True)
                return
            await send_indicator_step(user_id, context, msg=query.message)
        else:
            ob["symbols"].discard(item) if item in ob["symbols"] else ob["symbols"].add(item)
            await query.edit_message_reply_markup(build_toggle_keyboard(SYMBOLS, ob["symbols"], "sym"))

    elif data.startswith("pat_"):
        item = data[4:]
        if item == "CONFIRM":
            if not ob["patterns"]:
                await query.answer("Select at least one indicator!", show_alert=True)
                return
            await send_timeframe_step(user_id, context, msg=query.message)
        else:
            ob["patterns"].discard(item) if item in ob["patterns"] else ob["patterns"].add(item)
            await query.edit_message_reply_markup(build_toggle_keyboard(ALL_PATTERNS, ob["patterns"], "pat"))

    elif data.startswith("tf_"):
        item = data[3:]
        if item == "CONFIRM":
            if not ob["timeframes"]:
                await query.answer("Select at least one timeframe!", show_alert=True)
                return
            save_preferences(user_id, ob["symbols"], ob["patterns"], ob["timeframes"])
            await query.edit_message_text(
                build_setup_summary(ob["symbols"], ob["patterns"], ob["timeframes"]),
                parse_mode="Markdown"
            )
            onboarding.pop(user_id, None)
        else:
            ob["timeframes"].discard(item) if item in ob["timeframes"] else ob["timeframes"].add(item)
            await query.edit_message_reply_markup(build_toggle_keyboard(TIMEFRAMES, ob["timeframes"], "tf"))


# ══════════════════════════════════════════════════════════════════════════════
#  MENU BUTTON HANDLER
# ══════════════════════════════════════════════════════════════════════════════

async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        await update.message.delete()
    except Exception:
        pass
    if text == "📊 Zones":
        await zones_cmd(update, context)
    elif text == "⚙️ Settings":
        await reset(update, context)
    elif text == "ℹ️ Status":
        await status_cmd(update, context)
    elif text == "❓ Help":
        await help_cmd(update, context)
    elif text == "⏸ Stop":
        await stop_cmd(update, context)
    elif text == "▶️ Resume":
        await resume_cmd(update, context)
    elif text == "🔥 Confluence":
        await confluence_cmd(update, context)
