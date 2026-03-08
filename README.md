# Trillion Strategy Alert Bot

ICT pattern scanner + classic TA channel alerts for Telegram.

## Architecture

```
bot.py              — main bot, commands, onboarding, scanner loop
scanner.py          — ICT pattern detection (FVG, OB, BOS, CHoCH, Swings, Sweeps)
classic_scanner.py  — classic TA channel alerts (RSI, orderbook, candle patterns)
interpret.py        — market interpretation module
database.py         — SQLite user storage, subscriptions
payments.py         — CryptoBot payment integration
config.py           — configuration via environment variables
```

## Setup

1. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python bot.py
```

## Environment Variables

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather |
| `CRYPTOBOT_TOKEN` | Token from @CryptoBot (for payments) |
| `OWNER_IDS` | Comma-separated Telegram user IDs with lifetime access |
| `CHANNEL_ID` | Telegram channel ID for classic TA alerts |

## Channel Alerts (Trillion Strategy)

Posts automatically on candle close for BTCUSDT and ETHUSDT:

- **RSI alerts** — overbought/oversold grouped by symbol
- **Pattern alerts** — Pinbar/Predict with orderbook analysis
- **Setup alerts** — Scalp/Trend Long/Short with entry, SL, TP
- **Bounce alerts** — possible bounce/pullback signals
- **CME close** — weekly BTC CME futures close price

## Bot Features

- ICT pattern detection: FVG, IFVG, OB, BOS, CHoCH, Swings, Sweeps, Volume, PD zones
- Signal quality rating ★☆☆☆☆ — ★★★★★
- Per-user symbol, timeframe and pattern preferences
- Monthly subscription via CryptoBot (crypto payments)
- Owner lifetime access

## Security

- All secrets stored in `.env` file
- `.env` is excluded from git via `.gitignore`
- Never commit real tokens to the repository
