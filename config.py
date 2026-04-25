import os
from dotenv import load_dotenv
from timeframes import EXECUTION_HTF_MAP, MODEL_3_HTF_MAP, MODEL_3_LTF_MAP, SUPPORTED_TIMEFRAMES

load_dotenv()

# ── Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ── Binance Futures symbols
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XAUUSDT", "XAGUSDT"]

# ── Timeframes
TIMEFRAMES = SUPPORTED_TIMEFRAMES

# Entry model HTF/LTF behavior
REQUIRE_HTF_CONTEXT_FOR_ENTRY_MODELS = True
ENTRY_MODEL_HTF_MODE = os.getenv("ENTRY_MODEL_HTF_MODE", "strict")  # strict | soft | off
DISPLACEMENT_MIN_BODY_RATIO = 0.55
DISPLACEMENT_MIN_RANGE_EXPANSION = 1.2
DISPLACEMENT_FVG_BONUS = 0.25
SWING_INTERMEDIATE_RANGE_MULT = 1.1
SWING_LONG_MIN_AGE_BARS = 20
MODEL3_FILL_THRESHOLD = 0.5
MIN_RISK_BPS = 5
MAX_SETUP_AGE_BARS = 30
MAX_INVERSION_AGE_BARS = 40

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

# ── Welcome photo (absolute path; set env to "" to disable)
_default_photo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "welcome.jpg")
WELCOME_PHOTO = os.getenv("WELCOME_PHOTO", _default_photo)
