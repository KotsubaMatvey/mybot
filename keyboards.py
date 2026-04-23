"""Telegram keyboard builders."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

MENU_ACTIONS = {
    "zones": "ZONES",
    "status": "STATUS",
    "settings": "SETTINGS",
    "sessions": "SESSIONS",
    "charts": "CHARTS",
    "stop": "STOP",
    "resume": "RESUME",
    "help": "HELP",
}


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(MENU_ACTIONS["zones"]), KeyboardButton(MENU_ACTIONS["status"])],
        [
            KeyboardButton(MENU_ACTIONS["settings"]),
            KeyboardButton(MENU_ACTIONS["sessions"]),
            KeyboardButton(MENU_ACTIONS["charts"]),
        ],
        [KeyboardButton(MENU_ACTIONS["stop"]), KeyboardButton(MENU_ACTIONS["resume"])],
        [KeyboardButton(MENU_ACTIONS["help"])],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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


__all__ = [
    "MENU_ACTIONS",
    "build_toggle_keyboard",
    "confirm_stop_keyboard",
    "main_menu",
    "payment_keyboard",
]
