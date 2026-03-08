"""
CryptoBot payment integration.
Docs: https://help.crypt.bot/crypto-pay-api
"""
import aiohttp
import logging
from config import CRYPTOBOT_TOKEN

logger = logging.getLogger(__name__)

CRYPTOBOT_API      = "https://pay.crypt.bot/api"
SUBSCRIPTION_PRICE = "29.99"
SUBSCRIPTION_DAYS  = 30
ACCEPTED_ASSETS    = ["USDT", "TON", "BTC", "ETH", "LTC", "BNB", "TRX", "USDC"]

# ── Config validation — fail loudly at import time, not at runtime
if not CRYPTOBOT_TOKEN:
    logger.critical(
        "CRYPTOBOT_TOKEN is not set. "
        "Add it to your .env file. "
        "Payment functions will return None until this is fixed."
    )

_PAYMENTS_ENABLED = bool(CRYPTOBOT_TOKEN)


def _headers() -> dict:
    return {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}


async def create_invoice(user_id: int) -> dict | None:
    """
    Create a multi-currency invoice.
    Returns {"invoice_id": int, "pay_url": str} or None.

    Returns None immediately if CRYPTOBOT_TOKEN is not configured.
    """
    if not _PAYMENTS_ENABLED:
        logger.error("create_invoice called but CRYPTOBOT_TOKEN is not set — skipping")
        return None

    # Try fiat-pegged invoice first (payer chooses crypto, amount auto-converts)
    payload_fiat = {
        "currency_type":   "fiat",
        "fiat":            "USD",
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
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()

        if data.get("ok"):
            inv = data["result"]
            return {"invoice_id": inv["invoice_id"], "pay_url": inv["pay_url"]}

        # Fallback: fixed USDT invoice
        logger.warning(f"Fiat invoice failed, falling back to USDT: {data}")
        payload_usdt = {
            "asset":           "USDT",
            "amount":          SUBSCRIPTION_PRICE,
            "description":     "ICT Crypto Alerts — 30 day subscription",
            "payload":         str(user_id),
            "allow_comments":  False,
            "allow_anonymous": False,
            "expires_in":      3600,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload_usdt,
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()

        if data.get("ok"):
            inv = data["result"]
            return {"invoice_id": inv["invoice_id"], "pay_url": inv["pay_url"]}

        logger.error(f"CryptoBot createInvoice failed: {data}")
        return None

    except Exception as e:
        logger.error(f"CryptoBot request error: {e}")
        return None


async def check_invoice(invoice_id: int) -> bool:
    """Returns True if invoice is paid. Returns False immediately if token not set."""
    if not _PAYMENTS_ENABLED:
        logger.error("check_invoice called but CRYPTOBOT_TOKEN is not set — skipping")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CRYPTOBOT_API}/getInvoices",
                params={"invoice_ids": invoice_id},
                headers=_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()

        if data.get("ok"):
            items = data["result"].get("items", [])
            return bool(items and items[0]["status"] == "paid")

        logger.error(f"CryptoBot getInvoices error: {data}")
        return False

    except Exception as e:
        logger.error(f"CryptoBot check error: {e}")
        return False
