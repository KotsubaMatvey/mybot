"""
payment_flow.py — Telegram payment screen and callback handling
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import upsert_user, is_subscribed, set_subscription, get_subscription_status
from payments import create_invoice, check_invoice, SUBSCRIPTION_PRICE
from keyboards import payment_keyboard, main_menu
from formatters import build_payment_message
import onboarding

logger = logging.getLogger(__name__)

# Pending invoice tracking: {user_id: invoice_id}
_pending: dict = {}


async def send_payment_screen(user_id: int, context, update=None, expired: bool = False):
    """Create invoice and send payment message. Works both from commands and background."""
    inv = await create_invoice(user_id)
    if not inv:
        text = "❌ *Payment system unavailable*\n\n_Please try again later or contact support._"
        if update:
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await context.bot.send_message(user_id, text, parse_mode="Markdown")
        return

    _pending[user_id] = inv["invoice_id"]
    upsert_user(user_id, invoice_id=inv["invoice_id"])

    text = build_payment_message(SUBSCRIPTION_PRICE, expired)
    kb   = payment_keyboard(inv["pay_url"], inv["invoice_id"], SUBSCRIPTION_PRICE)

    if update:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await context.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=kb)


async def handle_callback(user_id: int, data: str, query, context) -> bool:
    """
    Handle payment callbacks.
    Returns True if consumed.
    """
    if not data.startswith("check_pay_"):
        return False

    invoice_id = int(data.split("_")[2])
    paid = await check_invoice(invoice_id)

    if paid:
        set_subscription(user_id, 30)
        _pending.pop(user_id, None)
        await query.edit_message_text(
            "✅ *Payment confirmed!*\n\n_Your 30-day subscription is now active._",
            parse_mode="Markdown"
        )
        onboarding.init(user_id)
        await context.bot.send_message(
            user_id,
            "Let's set up your preferences:",
            reply_markup=main_menu()
        )
        await onboarding.send_step_symbols(user_id, context)
    else:
        await query.answer(
            "Payment not found yet. Complete payment and try again.",
            show_alert=True
        )
    return True


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
