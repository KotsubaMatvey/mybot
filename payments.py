"""
CryptoBot payment integration.
Docs: https://help.crypt.bot/crypto-pay-api
"""
import aiohttp
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

CRYPTOBOT_API      = "https://pay.crypt.bot/api"
SUBSCRIPTION_PRICE = "29.99"
SUBSCRIPTION_DAYS  = 30

# Accepted currencies — CryptoBot supports all of these
ACCEPTED_ASSETS = ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"]

# Set this in config.py
CRYPTOBOT_TOKEN = ""


async def create_invoice(user_id: int) -> dict | None:
    """
    Create a multi-currency invoice.
    CryptoBot will show the payer a currency selector automatically
    when currency_type=fiat and fiat=USD is used — payer picks their crypto.
    Falls back to USDT-only if fiat mode unavailable.
    """
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}

    # Try fiat-pegged invoice first (payer chooses crypto, amount auto-converts)
    payload_fiat = {
        "currency_type": "fiat",
        "fiat":          "USD",
        "accepted_assets": ",".join(ACCEPTED_ASSETS),
        "amount":          SUBSCRIPTION_PRICE,
        "description":     "ICT Crypto Alerts — 30 day subscription",
        "payload":         str(user_id),
        "allow_comments":  False,
        "allow_anonymous": False,
        "expires_in":      3600,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload_fiat,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
        if data.get("ok"):
            inv = data["result"]
            return {"invoice_id": inv["invoice_id"], "pay_url": inv["pay_url"]}

        # Fallback: fixed USDT invoice
        logger.warning(f"Fiat invoice failed, falling back to USDT: {data}")
        payload_usdt = {
            "asset":         "USDT",
            "amount":        SUBSCRIPTION_PRICE,
            "description":   "ICT Crypto Alerts — 30 day subscription",
            "payload":       str(user_id),
            "allow_comments":  False,
            "allow_anonymous": False,
            "expires_in":      3600,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload_usdt,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
        if data.get("ok"):
            inv = data["result"]
            return {"invoice_id": inv["invoice_id"], "pay_url": inv["pay_url"]}

        logger.error(f"CryptoBot createInvoice error: {data}")
        return None
    except Exception as e:
        logger.error(f"CryptoBot request error: {e}")
        return None


async def check_invoice(invoice_id: int) -> bool:
    """Returns True if invoice is paid."""
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params  = {"invoice_ids": invoice_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CRYPTOBOT_API}/getInvoices",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
        if data.get("ok"):
            items = data["result"].get("items", [])
            if items and items[0]["status"] == "paid":
                return True
        return False
    except Exception as e:
        logger.error(f"CryptoBot check error: {e}")
        return False
