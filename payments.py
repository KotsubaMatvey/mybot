"""CryptoBot payment integration."""
from __future__ import annotations

import logging

import aiohttp

from config import CRYPTOBOT_TOKEN

logger = logging.getLogger(__name__)

CRYPTOBOT_API = "https://pay.crypt.bot/api"
SUBSCRIPTION_PRICE = "29.99"
SUBSCRIPTION_DAYS = 30
ACCEPTED_ASSETS = ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"]
_PAYMENTS_ENABLED = bool(CRYPTOBOT_TOKEN)

if not CRYPTOBOT_TOKEN:
    logger.critical(
        "CRYPTOBOT_TOKEN is not set. Add it to .env. Payment calls will degrade safely."
    )


def _headers() -> dict[str, str]:
    return {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}


async def create_invoice(user_id: int) -> dict | None:
    """Create a multi-currency invoice. Returns None if payments are unavailable."""
    if not _PAYMENTS_ENABLED:
        logger.error("create_invoice called while payments are disabled")
        return None

    payload_fiat = {
        "currency_type": "fiat",
        "fiat": "USD",
        "accepted_assets": ",".join(ACCEPTED_ASSETS),
        "amount": SUBSCRIPTION_PRICE,
        "description": "ICT Crypto Alerts - 30 day subscription",
        "payload": str(user_id),
        "allow_comments": False,
        "allow_anonymous": False,
        "expires_in": 3600,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload_fiat,
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                data = await response.json()

        if data.get("ok"):
            invoice = data["result"]
            return {"invoice_id": invoice["invoice_id"], "pay_url": invoice["pay_url"]}

        logger.warning("Fiat invoice failed, falling back to USDT: %s", data)
        payload_usdt = {
            "asset": "USDT",
            "amount": SUBSCRIPTION_PRICE,
            "description": "ICT Crypto Alerts - 30 day subscription",
            "payload": str(user_id),
            "allow_comments": False,
            "allow_anonymous": False,
            "expires_in": 3600,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload_usdt,
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                data = await response.json()
        if data.get("ok"):
            invoice = data["result"]
            return {"invoice_id": invoice["invoice_id"], "pay_url": invoice["pay_url"]}

        logger.error("CryptoBot createInvoice failed: %s", data)
        return None
    except Exception as exc:
        logger.error("CryptoBot request error: %s", exc)
        return None


async def check_invoice(invoice_id: int) -> bool:
    """Return True if the invoice has been paid."""
    if not _PAYMENTS_ENABLED:
        logger.error("check_invoice called while payments are disabled")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CRYPTOBOT_API}/getInvoices",
                params={"invoice_ids": invoice_id},
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                data = await response.json()
        if data.get("ok"):
            items = data["result"].get("items", [])
            return bool(items and items[0]["status"] == "paid")
        logger.error("CryptoBot getInvoices error: %s", data)
        return False
    except Exception as exc:
        logger.error("CryptoBot check error: %s", exc)
        return False


__all__ = [
    "ACCEPTED_ASSETS",
    "SUBSCRIPTION_DAYS",
    "SUBSCRIPTION_PRICE",
    "check_invoice",
    "create_invoice",
]
