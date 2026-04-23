"""Telegram keyboard builders."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton("ZONES"), KeyboardButton("STATUS")],
        [KeyboardButton("SETTINGS"), KeyboardButton("SESSIONS"), KeyboardButton("CHARTS")],
        [KeyboardButton("STOP"), KeyboardButton("RESUME")],
        [KeyboardButton("HELP")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)


def build_toggle_keyboard(items, selected, prefix) -> InlineKeyboardMarkup:
    rows = []
    for item in items:
        label = f"{item}  OK" if item in selected else item
        rows.append([InlineKeyboardButton(label, callback_data=f"{prefix}_{item}")])
    rows.append([InlineKeyboardButton("Confirm", callback_data=f"{prefix}_CONFIRM")])
    return InlineKeyboardMarkup(rows)


def confirm_stop_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Yes, pause", callback_data="stop_confirm"),
            InlineKeyboardButton("Cancel", callback_data="stop_cancel"),
        ]]
    )


def payment_keyboard(pay_url: str, invoice_id: int, price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Pay ${price} - Choose Crypto", url=pay_url)],
            [InlineKeyboardButton("Check Payment", callback_data=f"check_pay_{invoice_id}")],
        ]
    )
