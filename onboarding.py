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
from scanner import PRIMITIVE_PATTERNS, STRATEGY_PATTERNS

logger = logging.getLogger(__name__)

# In-memory state: {user_id: {symbols, patterns, timeframes, entry_models, trade_directions}}
_state: dict = {}
TRADE_DIRECTIONS = ["long", "short"]


def init(user_id: int):
    _state[user_id] = {
        "symbols": set(),
        "patterns": set(),
        "timeframes": set(),
        "entry_models": set(),
        "trade_directions": set(),
    }


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
    kb   = build_toggle_keyboard(PRIMITIVE_PATTERNS, sel, "pat")
    text = "Select primitive alerts:"
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


async def send_step_models(chat_id, context, msg=None):
    sel = _state.get(chat_id, {}).get("entry_models", set())
    kb = build_toggle_keyboard(STRATEGY_PATTERNS, sel, "model")
    text = "Select entry models:"
    if msg:
        await msg.edit_text(text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id, text, reply_markup=kb)


async def send_step_directions(chat_id, context, msg=None):
    sel = _state.get(chat_id, {}).get("trade_directions", set())
    kb = build_toggle_keyboard(TRADE_DIRECTIONS, sel, "dir")
    text = "Select strategy directions:"
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
            await query.answer()
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
            await query.answer()
            ob["patterns"].discard(item) if item in ob["patterns"] else ob["patterns"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(PRIMITIVE_PATTERNS, ob["patterns"], "pat")
            )
        return True

    if data.startswith("tf_"):
        item = data[3:]
        if item == "CONFIRM":
            if not ob["timeframes"]:
                await query.answer("Select at least one timeframe!", show_alert=True)
            else:
                await query.answer()
                await send_step_models(user_id, context)
        else:
            await query.answer()
            ob["timeframes"].discard(item) if item in ob["timeframes"] else ob["timeframes"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(TIMEFRAMES, ob["timeframes"], "tf")
            )
        return True

    if data.startswith("model_"):
        item = data[6:]
        if item == "CONFIRM":
            if not ob["entry_models"]:
                await query.answer("Select at least one entry model!", show_alert=True)
            else:
                await query.answer()
                await send_step_directions(user_id, context)
        else:
            await query.answer()
            ob["entry_models"].discard(item) if item in ob["entry_models"] else ob["entry_models"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(STRATEGY_PATTERNS, ob["entry_models"], "model")
            )
        return True

    if data.startswith("dir_"):
        item = data[4:]
        if item == "CONFIRM":
            if not ob["trade_directions"]:
                await query.answer("Select at least one direction!", show_alert=True)
            else:
                save_preferences(
                    user_id,
                    ob["symbols"],
                    ob["patterns"],
                    ob["timeframes"],
                    entry_models=ob["entry_models"],
                    trade_directions=ob["trade_directions"],
                )
                summary = build_setup_summary(
                    ob["symbols"],
                    ob["patterns"],
                    ob["timeframes"],
                    ob["entry_models"],
                    ob["trade_directions"],
                )
                await query.answer()
                await context.bot.send_message(user_id, summary, parse_mode="Markdown")
                clear(user_id)
        else:
            await query.answer()
            ob["trade_directions"].discard(item) if item in ob["trade_directions"] else ob["trade_directions"].add(item)
            await query.edit_message_reply_markup(
                build_toggle_keyboard(TRADE_DIRECTIONS, ob["trade_directions"], "dir")
            )
        return True

    return False
