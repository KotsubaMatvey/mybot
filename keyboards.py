"""
keyboards.py — all Telegram keyboard builders
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import SYMBOLS, TIMEFRAMES
from scanner import ALL_PATTERNS


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


def payment_keyboard(pay_url: str, invoice_id: int, price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(f"💳 Pay ${price} — Choose Crypto", url=pay_url),
    ], [
        InlineKeyboardButton("✅ Check Payment", callback_data=f"check_pay_{invoice_id}"),
    ]])
