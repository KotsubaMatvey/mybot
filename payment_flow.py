"""Telegram payment screen and payment callback handling."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

import onboarding
from database import get_subscription_status, get_user, is_subscribed, set_subscription, upsert_user
from formatters import build_payment_message
from keyboards import main_menu, payment_keyboard
from payments import SUBSCRIPTION_DAYS, SUBSCRIPTION_PRICE, check_invoice, create_invoice

logger = logging.getLogger(__name__)

_pending: dict[int, int] = {}


async def send_payment_screen(user_id: int, context, update=None, expired: bool = False) -> None:
    invoice = await create_invoice(user_id)
    if not invoice:
        text = "*Payment system unavailable*\n\n_Please try again later or contact support._"
        if update:
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await context.bot.send_message(user_id, text, parse_mode="Markdown")
        return

    _pending[user_id] = invoice["invoice_id"]
    upsert_user(user_id, invoice_id=invoice["invoice_id"])

    text = build_payment_message(SUBSCRIPTION_PRICE, expired)
    keyboard = payment_keyboard(invoice["pay_url"], invoice["invoice_id"], SUBSCRIPTION_PRICE)

    if update:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await context.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_callback(user_id: int, data: str, query, context) -> bool:
    if not data.startswith("check_pay_"):
        return False

    try:
        invoice_id = int(data.split("_")[2])
    except (IndexError, ValueError):
        await query.answer("Invalid payment request.", show_alert=True)
        return True

    user = get_user(user_id)
    expected_invoice = user.get("invoice_id") if user else None
    if expected_invoice and invoice_id != expected_invoice:
        await query.answer("This payment link is outdated. Request a new invoice.", show_alert=True)
        return True

    if await check_invoice(invoice_id):
        await query.answer()
        set_subscription(user_id, SUBSCRIPTION_DAYS)
        _pending.pop(user_id, None)
        upsert_user(user_id, invoice_id=None)
        await query.edit_message_text(
            f"*Payment confirmed!*\n\n_Your {SUBSCRIPTION_DAYS}-day subscription is now active._",
            parse_mode="Markdown",
        )
        onboarding.init(user_id)
        await context.bot.send_message(user_id, "Let's set up your preferences:", reply_markup=main_menu())
        await onboarding.send_step_symbols(user_id, context)
    else:
        await query.answer("Payment not found yet. Complete payment and try again.", show_alert=True)
    return True


async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    upsert_user(user_id)
    if is_subscribed(user_id):
        status = get_subscription_status(user_id)
        await update.message.reply_text(f"*Subscription*\n\n{status}", parse_mode="Markdown")
        return
    await send_payment_screen(user_id, context, update)


__all__ = ["handle_callback", "is_subscribed", "pay_cmd", "send_payment_screen"]
