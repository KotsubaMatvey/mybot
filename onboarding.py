"""
onboarding.py — multi-step setup flow state machine
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import save_preferences
from keyboards import build_toggle_keyboard
from formatters import build_setup_summary
from config import SYMBOLS, TIMEFRAMES
from scanner import ALL_PATTERNS

logger = logging.getLogger(__name__)

# In-memory state: {user_id: {symbols, patterns, timeframes}}
_state: dict = {}


def init(user_id: int):
    _state[user_id] = {"symbols": set(), "patterns": set(), "timeframes": set()}


def is_active(user_id: int) -> bool:
    return user_id in _state


def clear(user_id: int):
    _state.pop(user_id, None)


async def send_step_symbols(chat_id, context, msg=None):
    sel  = _state.get(chat_id, {}).get("symbols", set())
    kb   = build_toggle_keyboard(SYMBOLS, sel, "sym")
    text = "Select symbols:"
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, reply_markup=kb)


async def send_step_indicators(chat_id, context, msg=None):
    sel  = _state.get(chat_id, {}).get("patterns", set())
    kb   = build_toggle_keyboard(ALL_PATTERNS, sel, "pat")
    text = "Select indicators:"
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, reply_markup=kb)


async def send_step_timeframes(chat_id, context, msg=None):
    sel  = _state.get(chat_id, {}).get("timeframes", set())
    kb   = build_toggle_keyboard(TIMEFRAMES, sel, "tf")
    text = "Select timeframes:"
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, reply_markup=kb)


async def handle_callback(user_id: int, data: str, query, context) -> bool:
    """
    Handle onboarding callbacks.
    Returns True if the callback was consumed, False if not an onboarding event.
    """
    if not is_active(user_id):
        return False

    ob = _state[user_id]

    if data.startswith("sym_"):
        item = data[4:]
        if item == "CONFIRM":
            if not ob["symbols"]:
                await query.answer("Select at least one symbol!", show_alert=True)
            else:
                await query.answer()
                await send_step_indicators(user_id, context)
        else:
            ob["symbols"].discard(item) if item in ob["symbols"] else ob["symbols"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(SYMBOLS, ob["symbols"], "sym")
            )
        return True

    if data.startswith("pat_"):
        item = data[4:]
        if item == "CONFIRM":
            if not ob["patterns"]:
                await query.answer("Select at least one indicator!", show_alert=True)
            else:
                await query.answer()
                await send_step_timeframes(user_id, context)
        else:
            ob["patterns"].discard(item) if item in ob["patterns"] else ob["patterns"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(ALL_PATTERNS, ob["patterns"], "pat")
            )
        return True

    if data.startswith("tf_"):
        item = data[3:]
        if item == "CONFIRM":
            if not ob["timeframes"]:
                await query.answer("Select at least one timeframe!", show_alert=True)
            else:
                save_preferences(user_id, ob["symbols"], ob["patterns"], ob["timeframes"])
                summary = build_setup_summary(ob["symbols"], ob["patterns"], ob["timeframes"])
                await query.answer()
                await context.bot.send_message(user_id, summary, parse_mode="Markdown")
                clear(user_id)
        else:
            ob["timeframes"].discard(item) if item in ob["timeframes"] else ob["timeframes"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(TIMEFRAMES, ob["timeframes"], "tf")
            )
        return True

    return False
