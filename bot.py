"""
ICT Crypto Alerts Bot v3 — clean UI + channel insights
"""
import asyncio
import logging
from datetime import datetime, timezone
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from scanner import run_scanner, get_active_zones, ALL_PATTERNS, score_to_stars
from database import (
    init_db, get_user, upsert_user, get_all_active_users,
    save_preferences, set_active,
    is_subscribed, set_subscription, get_subscription_status, set_owner
)
from payments import create_invoice, check_invoice, SUBSCRIPTION_PRICE
from interpret import pattern_to_interpretation
from config import TELEGRAM_BOT_TOKEN, SYMBOLS, TIMEFRAMES, SCAN_INTERVAL, DIGEST_INTERVAL, OWNER_IDS, CHANNEL_ID
from classic_scanner import channel_scheduler

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

onboarding: dict = {}
signals_today: dict = {}
pending_payments: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")

def score_label(score: int) -> str:
    stars = "★" * score + "☆" * (5 - score)
    labels = {0: "", 1: "Weak", 2: "Moderate", 3: "Good", 4: "Strong", 5: "Excellent"}
    label = labels.get(score, "")
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


# ══════════════════════════════════════════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════════════════════════════════════════

def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton("📊 Zones"),    KeyboardButton("ℹ️ Status")],
        [KeyboardButton("⚙️ Settings"), KeyboardButton("🔥 Confluence")],
        [KeyboardButton("⏸ Stop"),      KeyboardButton("▶️ Resume")],
        [KeyboardButton("❓ Help")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def build_toggle_keyboard(items, selected, prefix) -> InlineKeyboardMarkup:
    kb = []
    for item in items:
        label = f"✅  {item}" if item in selected else f"◻️  {item}"
        kb.append([InlineKeyboardButton(label, callback_data=f"{prefix}_{item}")])
    kb.append([InlineKeyboardButton("✔️  Confirm", callback_data=f"{prefix}_CONFIRM")])
    return InlineKeyboardMarkup(kb)

def confirm_stop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⏸ Yes, pause", callback_data="stop_confirm"),
        InlineKeyboardButton("✖ Cancel",     callback_data="stop_cancel"),
    ]])


# ══════════════════════════════════════════════════════════════════════════════
#  ONBOARDING
# ══════════════════════════════════════════════════════════════════════════════

def init_onboarding(user_id: int):
    onboarding[user_id] = {"symbols": set(), "patterns": set(), "timeframes": set()}

async def send_symbol_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("symbols", set())
    kb   = build_toggle_keyboard(SYMBOLS, sel, "sym")
    text = f"*Step 1 of 3 — Symbols*\n\nSelect the pairs you want to track:"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

async def send_indicator_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("patterns", set())
    kb   = build_toggle_keyboard(ALL_PATTERNS, sel, "pat")
    text = f"*Step 2 of 3 — Indicators*\n\nSelect which patterns to detect:"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

async def send_timeframe_step(chat_id, context, msg=None):
    sel  = onboarding.get(chat_id, {}).get("timeframes", set())
    kb   = build_toggle_keyboard(TIMEFRAMES, sel, "tf")
    text = f"*Step 3 of 3 — Timeframes*\n\nSelect timeframes:\n_Tip: 15m + 1h + 4h covers most ICT setups_"
    if msg:
        await msg.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

def setup_summary_card(symbols, patterns, timeframes) -> str:
    return (
        f"✅ *Setup Complete*\n\n"
        f"*Symbols*\n`{'  ·  '.join(sorted(symbols))}`\n\n"
        f"*Indicators*\n`{'  ·  '.join(sorted(patterns))}`\n\n"
        f"*Timeframes*\n`{'  ·  '.join(sorted(timeframes))}`\n\n"
        "\n"
        "_Alerts will arrive automatically._\n"
        "_Tap_ 📊 *Zones* _to see active setups now._"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAYMENT
# ══════════════════════════════════════════════════════════════════════════════

async def send_payment_screen(user_id, context, update=None, expired=False):
    inv = await create_invoice(user_id)
    if not inv:
        text = f"❌ *Payment system unavailable*\n\n_Please try again later._"
        if update:
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await context.bot.send_message(user_id, text, parse_mode="Markdown")
        return

    pending_payments[user_id] = inv["invoice_id"]
    upsert_user(user_id, invoice_id=inv["invoice_id"])

    expired_line = "\n⚠️ _Your subscription has expired._\n" if expired else ""
    text = (
        f"💳 *Subscribe to ICT Crypto Alerts*\n"
        f"{expired_line}\n"
        f"*Price:*  `${SUBSCRIPTION_PRICE}` / month\n"
        f"_Pay in any crypto — USDT · TON · BTC · ETH_\n\n"
        f"*Includes:*\n"
        f"▪ Real-time ICT pattern alerts\n"
        f"▪ FVG · IFVG · OB · BOS · CHoCH · Swings\n"
        f"▪ Signal quality rating ★★★★★\n"
        f"▪ Market interpretations\n"
        f"▪ Access to insights channel\n\n"
        "\n"
        f"_After payment tap_ ✅ *Check Payment* _below._"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"💳 Pay ${SUBSCRIPTION_PRICE} — Choose Crypto", url=inv["pay_url"]),
    ],[
        InlineKeyboardButton("✅ Check Payment", callback_data=f"check_pay_{inv['invoice_id']}"),
    ]])
    if update:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=kb)


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


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

async def send_dashboard(user_id: int, context, update=None):
    user       = get_user(user_id)
    zones      = get_active_zones()
    today      = signals_today.get(user_id, 0)
    status     = "Active" if user["active"] else "Paused"
    conf       = "ON" if user.get("confluence", True) else "OFF"
    sub_status = get_subscription_status(user_id)

    zone_count = sum(
        1 for sym in user["symbols"]
        for tf, patterns in zones.get(sym, {}).items()
        if tf in user["timeframes"]
        for p in patterns if p["type"] in user["patterns"]
    )
    syms_str = "  ·  ".join(sorted(user["symbols"]))
    tfs_str  = "  ·  ".join(sorted(user["timeframes"]))

    text = (
        f"📡 *ICT Crypto Alerts*\n\n"
        f"*Status:*  `{status}`\n"
        f"*Pairs:*  `{syms_str}`\n"
        f"*Timeframes:*  `{tfs_str}`\n"
        f"*Confluence:*  `{conf}`\n"
        f"*Subscription:*  {sub_status}\n\n"
        "\n"
        f"Last scan:  `{utc_now()}`\n"
        f"Active zones:  *{zone_count}*\n"
        f"Signals today:  *{today}*"
    )
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
        f"👋 *Welcome to ICT Crypto Alerts*\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "*Patterns:*\n"
        "`FVG · IFVG · OB · BOS · CHoCH`\n"
        "`Swings · Sweeps · Volume · PD`\n\n"
        "*Signal rating:*  ★☆☆☆☆ — ★★★★★\n\n"
        "\n"
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
        f"⚙️ *Reset Preferences*\n\n_Setting up from scratch._",
        parse_mode="Markdown"
    )
    await send_symbol_step(user_id, context)


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⏸ *Pause Alerts*\n\nAre you sure?",
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
        f"▶️ *Alerts Resumed*\n\n_You will now receive alerts._",
        parse_mode="Markdown"
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
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
    lines = [f"📊 *Active ICT Zones*"]
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
            f"📊 *Active ICT Zones*\n\n_No active zones. Scans run every 60s._",
            parse_mode="Markdown"
        )
        return
    lines += [f"", f"_Updated: {utc_now()}_"]
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
    text = (
        f"❓ *ICT Crypto Alerts — Help*\n\n"
        "*Commands*\n"
        "`/start`       Dashboard or setup\n"
        "`/pay`         Subscription & payment\n"
        "`/zones`       Active zones now\n"
        "`/status`      Subscription overview\n"
        "`/reset`       Change preferences\n"
        "`/confluence`  Toggle interpretations\n"
        "`/stop`        Pause alerts\n"
        "`/resume`      Resume alerts\n\n"
        "\n"
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

    if data.startswith("check_pay_"):
        invoice_id = int(data.split("_")[2])
        paid = await check_invoice(invoice_id)
        if paid:
            set_subscription(user_id, 30)
            pending_payments.pop(user_id, None)
            await query.edit_message_text(
                f"✅ *Payment confirmed!*\n\n"
                "_Your 30-day subscription is now active._",
                parse_mode="Markdown"
            )
            init_onboarding(user_id)
            await context.bot.send_message(
                user_id, f"Let's set up your preferences:",
                reply_markup=main_menu()
            )
            await send_symbol_step(user_id, context)
        else:
            await query.answer("Payment not found yet. Please complete payment and try again.", show_alert=True)
        return

    if data == "stop_confirm":
        set_active(user_id, False)
        await query.edit_message_text(
            f"⏸ *Alerts Paused*\n\n_Tap ▶️ Resume to restart._",
            parse_mode="Markdown"
        )
        return
    if data == "stop_cancel":
        await query.edit_message_text(
            f"*Cancelled*\n\n_Alerts remain active._",
            parse_mode="Markdown"
        )
        return

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
                setup_summary_card(ob["symbols"], ob["patterns"], ob["timeframes"]),
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


# ══════════════════════════════════════════════════════════════════════════════
#  ALERT FORMATTING — clean, no broken borders
# ══════════════════════════════════════════════════════════════════════════════

def build_alert_message(symbol: str, timeframe: str, patterns_meta: list, score: int = 0) -> str:
    rating = score_label(score)
    lines  = [
        f"*{symbol}  ·  {timeframe}*",
        f"_{rating}_",
        "",
    ]
    for p in patterns_meta:
        detail    = p.get("detail", "")
        hint      = pattern_hint(p.get("pattern", ""), p.get("direction", ""))
        lines.append(f"*{detail}*")
        if hint:
            lines.append(f"_{hint}_")
        lines.append("")
    lines.append(f"`{utc_now()}`")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════

def build_channel_insight(symbol: str, tf: str, patterns_meta: list, candles: list, score: int) -> str | None:
    """Build a channel post only for high-quality signals (score >= 3)."""
    if score < 3:
        return None
    if not candles:
        return None

    last_price = candles[-1]["close"]
    pattern_types = {p.get("pattern", "") for p in patterns_meta}
    directions    = [p.get("direction", "") for p in patterns_meta]

    bullish = directions.count("Bullish") + directions.count("High") + directions.count("Discount")
    bearish = directions.count("Bearish") + directions.count("Low")  + directions.count("Premium")
    direction = "bullish" if bullish >= bearish else "bearish"

    # Signal type
    if "CHoCH" in pattern_types:
        signal_label = "CHoCH — possible reversal"
        emoji = "⚡"
    elif "Sweeps" in pattern_types:
        signal_label = "Liquidity sweep"
        emoji = "🌊"
    elif "BOS" in pattern_types:
        signal_label = "Break of structure"
        emoji = "📐"
    elif "FVG" in pattern_types or "IFVG" in pattern_types:
        signal_label = "Fair value gap"
        emoji = "🎯"
    elif "OB" in pattern_types:
        signal_label = "Order block"
        emoji = "🧱"
    else:
        signal_label = "Pattern confluence"
        emoji = "🍀"

    dir_label = "Long" if direction == "bullish" else "Short"
    dir_emoji = "📈" if direction == "bullish" else "📉"

    # SL/TP from recent structure
    lookback = candles[-20:]
    hi = max(c["high"] for c in lookback)
    lo = min(c["low"]  for c in lookback)
    rng = hi - lo

    def fmt(p):
        return f"{p:,.2f}" if p > 100 else f"{p:.4f}"

    if direction == "bullish":
        sl  = round(lo - rng * 0.02, 4)
        tp1 = round(last_price + rng * 0.3, 4)
        tp2 = round(last_price + rng * 0.6, 4)
        tp3 = round(last_price + rng * 1.0, 4)
    else:
        sl  = round(hi + rng * 0.02, 4)
        tp1 = round(last_price - rng * 0.3, 4)
        tp2 = round(last_price - rng * 0.6, 4)
        tp3 = round(last_price - rng * 1.0, 4)

    rating = score_label(score)

    return (
        f"🍀 *{tf}  {dir_emoji}  {signal_label}  —  {dir_label}*\n"
        f"*#{symbol}*  ·  `{fmt(last_price)}`\n"
        f"_{rating}_\n\n"
        f"Entry: `{fmt(last_price)}`\n"
        f"Stop-loss: `{fmt(sl)}`\n\n"
        f"Targets:\n"
        f"▪ 30% at `{fmt(tp1)}`\n"
        f"▪ 30% at `{fmt(tp2)}`\n"
        f"▪ 40% at `{fmt(tp3)}`\n\n"
        f"`{utc_now()}`\n\n"
        f"⚠️ _Not financial advice_"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SCANNER LOOP
# ══════════════════════════════════════════════════════════════════════════════

async def scanner_loop(application: Application):
    logger.info("Scanner loop started")
    last_digest    = 0

    while True:
        try:
            alerts, confluences, all_candles = await run_scanner()
            users = get_all_active_users()
            now   = asyncio.get_event_loop().time()

            grouped_meta: dict = {}
            scores: dict       = {}
            for a in alerts:
                key = (a["symbol"], a["timeframe"])
                grouped_meta.setdefault(key, []).append(a)
                scores[key] = a.get("score", 0)


            for user in users:
                uid = user["user_id"]
                if not is_subscribed(uid):
                    continue

                for (symbol, tf), meta_list in grouped_meta.items():
                    if symbol not in user["symbols"] or tf not in user["timeframes"]:
                        continue
                    filtered = [m for m in meta_list if m["pattern"] in user["patterns"]]
                    if not filtered:
                        continue
                    score = scores.get((symbol, tf), 0)
                    try:
                        msg = build_alert_message(symbol, tf, filtered, score)
                        await application.bot.send_message(uid, msg, parse_mode="Markdown")
                        signals_today[uid] = signals_today.get(uid, 0) + 1
                    except Exception as e:
                        logger.error(f"Alert send error {uid}: {e}")

                if user.get("confluence", True):
                    sent_interp = set()
                    for (symbol, tf), meta_list in grouped_meta.items():
                        if symbol not in user["symbols"] or tf not in user["timeframes"]:
                            continue
                        if (symbol, tf) in sent_interp:
                            continue
                        filtered = [m for m in meta_list if m["pattern"] in user["patterns"]]
                        if not filtered:
                            continue
                        candles = all_candles.get((symbol, tf), [])
                        interp  = pattern_to_interpretation(filtered, candles, symbol, tf)
                        if interp:
                            try:
                                await application.bot.send_message(uid, interp, parse_mode="Markdown")
                                sent_interp.add((symbol, tf))
                            except Exception as e:
                                logger.error(f"Interp send error {uid}: {e}")



            if now - last_digest >= DIGEST_INTERVAL:
                last_digest = now
                if datetime.now(timezone.utc).hour == 0:
                    signals_today.clear()
                await send_digest(application, users)

        except Exception as e:
            logger.error(f"Scanner loop error: {e}")

        await asyncio.sleep(SCAN_INTERVAL)


async def send_digest(application: Application, users: list):
    zones = get_active_zones()
    if not zones:
        return
    for user in users:
        uid = user["user_id"]
        if not is_subscribed(uid):
            continue
        lines = [f"📋 *Hourly Digest  ·  {utc_now()}*"]
        has   = False
        for symbol in sorted(user["symbols"]):
            sym_lines = [f"\n*{symbol}*"]
            for tf in TIMEFRAMES:
                if tf not in user["timeframes"]:
                    continue
                for p in zones.get(symbol, {}).get(tf, []):
                    if p["type"] in user["patterns"]:
                        sym_lines.append(f"  `{tf}`  {p['detail']}")
                        has = True
            if len(sym_lines) > 1:
                lines.extend(sym_lines)
        if has:
            lines += [f"", f"_Signals today: {signals_today.get(uid, 0)}_"]
            try:
                await application.bot.send_message(uid, "\n".join(lines), parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Digest error {uid}: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

async def post_init(application: Application):
    asyncio.create_task(scanner_loop(application))
    if CHANNEL_ID:
        asyncio.create_task(channel_scheduler(application.bot, CHANNEL_ID))
        logger.info("Channel scheduler started")
    logger.info("Scanner task started")


def main():
    init_db()
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("pay",        pay_cmd))
    app.add_handler(CommandHandler("reset",      reset))
    app.add_handler(CommandHandler("stop",       stop_cmd))
    app.add_handler(CommandHandler("resume",     resume_cmd))
    app.add_handler(CommandHandler("status",     status_cmd))
    app.add_handler(CommandHandler("zones",      zones_cmd))
    app.add_handler(CommandHandler("confluence", confluence_cmd))
    app.add_handler(CommandHandler("help",       help_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_button_handler))

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
