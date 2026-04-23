# ICT Telegram Trading Bot

Python Telegram bot for Binance Futures market analysis.

## Architecture

```text
bot.py

handlers/
  __init__.py
  callbacks.py
  charts.py
  common.py
  core.py
  sessions.py

market_primitives/
  common.py
  liquidity.py
  structure.py
  fvg.py
  ifvg.py
  order_blocks.py
  levels.py
  volume.py
  pd.py
  smt.py

strategies/
  types.py
  scoring.py
  formatter.py
  entry_model_1.py
  entry_model_2.py
  entry_model_3.py

scanner/
  __init__.py
  engine.py
  snapshots.py
  cache.py
  dedup.py
  confluence.py
  scoring.py

presentation/
  types.py
  alert_builders.py
  chart_payloads.py
  formatters.py
```

## Features

- typed market primitives: swings, sweeps, BOS/CHOCH, FVG/IFVG, OB/breakers, EQH/EQL, PD, SMT, volume
- typed entry setups: Entry Model 1, Entry Model 2, Entry Model 3
- Telegram alerts with optional chart overlays
- onboarding with primitive/model/direction preferences
- SQLite persistence for subscriptions and user settings
- classic channel alerts kept separately from ICT setup engine

## Setup

1. Create `.env` with your bot and payment credentials.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the bot:

```bash
python bot.py
```

## Required Environment

- `TELEGRAM_BOT_TOKEN`
- `CRYPTOBOT_TOKEN`
- `OWNER_IDS`
- `CHANNEL_ID`

## Verification

- `python -m compileall .`
- `python offline_smoke_test.py`
- `python offline_backtest.py`
