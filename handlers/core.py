from __future__ import annotations

import logging

import onboarding
import payment_flow
from config import OWNER_IDS, TIMEFRAMES, WELCOME_PHOTO
from database import get_user, is_subscribed, set_active, set_owner, upsert_user
from formatters import utc_now

from .common import alert_enabled_for_user, send_dashboard, user_ready

logger = logging.getLogger(__name__)


async def start(update, context):
    user_id = update.effective_user.id
    upsert_user(user_id)
    if user_id in OWNER_IDS:
        set_owner(user_id)
    user = get_user(user_id)

    if user_ready(user):
        if is_subscribed(user_id):
            await send_dashboard(user_id, context, update)
            return
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return

    if user_id in OWNER_IDS or is_subscribed(user_id):
        onboarding.init(user_id)
        await update.message.reply_text(
            "Setup Preferences\n\nSelect symbols, primitive alerts, timeframes, entry models and directions."
        )
        await onboarding.send_step_symbols(user_id, context)
        return

    welcome_text = (
        "ICT Crypto Alerts\n\n"
        "Real-time ICT pattern scanner for Binance Futures.\n\n"
        "Primitives:\n"
        "FVG | IFVG | OB | BOS | CHoCH | Sweeps | Liquidity\n\n"
        "Strategies:\n"
        "Entry Model 1 | Entry Model 2 | Entry Model 3\n\n"
        "Market analysis tool. Not financial advice."
    )
    try:
        with open(WELCOME_PHOTO, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=welcome_text)
    except Exception:
        await update.message.reply_text(welcome_text)
    await payment_flow.send_payment_screen(user_id, context, update)


async def reset(update, context):
    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update)
        return
    onboarding.init(user_id)
    await update.message.reply_text("Reset Preferences\n\nSetting up from scratch.")
    await onboarding.send_step_symbols(user_id, context)


async def stop_cmd(update, context):
    from keyboards import confirm_stop_keyboard

    await update.message.reply_text("Pause Alerts\n\nAre you sure?", reply_markup=confirm_stop_keyboard())


async def resume_cmd(update, context):
    user = get_user(update.effective_user.id)
    if not user_ready(user):
        if is_subscribed(update.effective_user.id):
            await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        else:
            await update.message.reply_text("No subscription found. Send /start")
        return
    set_active(update.effective_user.id, True)
    await update.message.reply_text("Alerts resumed.\n\nYou will now receive alerts.")


async def status_cmd(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user_ready(user):
        if is_subscribed(user_id):
            await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        else:
            await update.message.reply_text("No active subscription. Send /start")
        return
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return
    await send_dashboard(user_id, context, update)


async def zones_cmd(update, context):
    from scanner import get_active_zones

    user_id = update.effective_user.id
    if not is_subscribed(user_id):
        await payment_flow.send_payment_screen(user_id, context, update, expired=True)
        return
    user = get_user(user_id)
    if not user_ready(user):
        await update.message.reply_text("Setup is not finished yet. Send /start or /reset.")
        return

    zones = get_active_zones()
    lines = ["Active ICT Zones"]
    has_alerts = False

    for symbol in sorted(user["symbols"]):
        symbol_lines = [f"\n{symbol}"]
        for timeframe in TIMEFRAMES:
            if timeframe not in user["timeframes"]:
                continue
            for alert in zones.get(symbol, {}).get(timeframe, []):
                if not alert_enabled_for_user(alert, user):
                    continue
                symbol_lines.append(f"  {timeframe}  {alert.detail}")
                has_alerts = True
        if len(symbol_lines) > 1:
            lines.extend(symbol_lines)

    if not has_alerts:
        await update.message.reply_text("Active ICT Zones\n\nNo active zones. Scans run every 60s.")
        return
    lines += ["", f"Updated: {utc_now()}"]
    await update.message.reply_text("\n".join(lines))


async def help_cmd(update, context):
    await update.message.reply_text(
        "ICT Crypto Alerts - Help\n\n"
        "Commands\n"
        "/start       Dashboard or setup\n"
        "/pay         Subscription and payment\n"
        "/zones       Active zones now\n"
        "/status      Subscription overview\n"
        "/reset       Change preferences\n"
        "/stop        Pause alerts\n"
        "/resume      Resume alerts\n"
        "/session     Current session\n"
        "/chart       Render a chart from cache\n\n"
        "Primitive alerts\n"
        "FVG  IFVG  OB  BOS  CHoCH  Sweeps  Liquidity  Breaker\n"
        "Swings  Volume  VP  KL  PD  EQH  EQL  SMT\n\n"
        "Entry models\n"
        "Entry Model 1  Entry Model 2  Entry Model 3\n\n"
        "Not financial advice."
    )


__all__ = [
    "help_cmd",
    "reset",
    "resume_cmd",
    "start",
    "status_cmd",
    "stop_cmd",
    "zones_cmd",
]
