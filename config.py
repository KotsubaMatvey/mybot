import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ── Binance Futures symbols
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# ── Timeframes
TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]

# ── Candles to fetch
CANDLE_LIMIT = 100

# ── Scanner interval (seconds)
SCAN_INTERVAL = 60

# ── Digest interval (seconds) — 1 hour
DIGEST_INTERVAL = 3600

# ── CryptoBot
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")

# ── Owner user IDs (permanent free access)
_owner_raw = os.getenv("OWNER_IDS", "")
OWNER_IDS = [int(x.strip()) for x in _owner_raw.split(",") if x.strip().isdigit()]

# ── Payment check interval (seconds)
PAYMENT_CHECK_INTERVAL = 30

# ── Insights channel
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
