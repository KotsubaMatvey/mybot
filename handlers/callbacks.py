from __future__ import annotations

import onboarding
import payment_flow
from keyboards import MENU_ACTIONS

from .charts import handle_chart_callback
from .core import help_cmd, reset, resume_cmd, status_cmd, stop_cmd, zones_cmd
from .sessions import sessions_cmd


async def callback_handler(update, context):
    from database import set_active

    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "stop_confirm":
        await query.answer()
        set_active(user_id, False)
        await query.edit_message_text("Alerts paused.\n\nTap Resume to restart.")
        return
    if data == "stop_cancel":
        await query.answer()
        await query.edit_message_text("Cancelled.\n\nAlerts remain active.")
        return
    if data.startswith("chart_"):
        await handle_chart_callback(update, context)
        return
    if await payment_flow.handle_callback(user_id, data, query, context):
        return
    if await onboarding.handle_callback(user_id, data, query, context):
        return
    await query.answer()
    await query.edit_message_text("Session expired. Tap /start")


async def menu_button_handler(update, context):
    from .charts import charts_cmd

    dispatch = {
        MENU_ACTIONS["zones"]: zones_cmd,
        MENU_ACTIONS["settings"]: reset,
        MENU_ACTIONS["status"]: status_cmd,
        MENU_ACTIONS["help"]: help_cmd,
        MENU_ACTIONS["stop"]: stop_cmd,
        MENU_ACTIONS["resume"]: resume_cmd,
        MENU_ACTIONS["sessions"]: sessions_cmd,
        MENU_ACTIONS["charts"]: charts_cmd,
    }
    handler = dispatch.get(update.message.text)
    if handler is None:
        return
    try:
        await update.message.delete()
    except Exception:
        pass
    await handler(update, context)


__all__ = ["callback_handler", "menu_button_handler"]
