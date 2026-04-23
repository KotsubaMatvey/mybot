from __future__ import annotations

import payment_flow
from database import toggle_sessions_alerts
from sessions import get_current_session_message


async def sessions_cmd(update, context):
    user_id = update.effective_user.id
    if not payment_flow.is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    new_state = toggle_sessions_alerts(user_id)
    state_text = "ON" if new_state else "OFF"
    current = await get_current_session_message()
    await update.message.reply_text(f"Session Alerts: {state_text}\n\n{current}")


async def session_status_cmd(update, context):
    current = await get_current_session_message()
    await update.message.reply_text(current)


__all__ = ["session_status_cmd", "sessions_cmd"]
