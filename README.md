Binance Statistical Arbitrage Bot with Telegram Integration

📌 Project Overview

This project implements a fully-automated statistical arbitrage trading bot on Binance USDT perpetual futures. It leverages cointegration-based pair trading and z-score thresholds to identify trading opportunities and sends real-time trade signals via Telegram. The project is modular, backtestable, and production-ready.

Purpose: To build a robust, data-driven crypto trading system suitable for real-time deployment and institutional-level analysis.

⚙️ Features

Cointegration Analysis: Automatically detects cointegrated pairs using ADF test and Kalman Filter-based dynamic hedge ratios.

Top Pair Selection: Ranks pairs using a composite scoring model (PCA-based) considering p-value, zero-crossings, z-score, etc.

Real-time Signal Generation: Monitors selected pairs every hour and triggers LONG/SHORT/EXIT signals based on z-score levels.

Telegram Alert Integration: Sends alerts for trade entry and exit via Telegram Bot with chat ID and token management via .env.

Backtesting Support: Includes z-score backtester and total portfolio return simulation.

Modular Design: Fully organized by component (cointegration.py, fetch_data.py, visualize.py, etc.).

🧠 Strategy Logic

Cointegration Screening (main.py):

Pulls OHLCV data from Binance using python-binance.

Tests all USDT futures pairs for cointegration.

Uses Kalman Filter to compute time-varying hedge ratio.

Saves top 5 statistically strongest pairs to CSV.

Signal Generation (telegram_message.py):

Every hour, fetches live prices and recalculates z-score for the top 5 pairs.

Entry condition:

Z > 2: SHORT first coin / LONG second coin

Z < -2: LONG first coin / SHORT second coin

Exit condition:

abs(Z) < 0.5: mean-reversion assumed complete

All signals are logged and sent via Telegram.

Position Tracking:

JSON file (open_positions.json) records current open pairs.

Prevents duplicate entry/exit messages.

Backtesting (zscore_backtest.py, total_backtest.py):

Tests spread-based entry/exit logic on historical data.

Supports multiple pairs and cumulative return analysis.

📊 Technology Stack

Language: Python 3.10+

Data Source: Binance Futures API (via python-binance)

Statistical Models:

ADF test (via statsmodels)

Kalman Filter (via pykalman)

Notification: Telegram Bot API (requests)

Configuration: Environment variables (python-dotenv)

🗂️ File Structure

binance-statistical-arbitrage-bot/

├── .env.example

├── .gitignore

├── cointegration.py

├── fetch_data.py

├── main.py

├── telegram_message.py

├── total_backtest.py

├── top5_cointegrated_pairs.csv

├── visualize.py

├── zscore_backtest.py

├── open_positions.json (ignored)

📦 How to Run

1. Clone the Repository

git clone https://github.com/yourusername/binance-statistical-arbitrage-bot.git
cd binance-statistical-arbitrage-bot

2. Install Requirements

pip install -r requirements.txt

3. Setup Environment Variables

Create a .env file based on .env.example:

BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

4. Run Main Screening Script

python main.py

5. Schedule Hourly Signal Monitoring

python telegram_message.py  # or run via crontab/Task Scheduler

📈 Example Telegram Alerts

[ADAUSDT - SOLUSDT]
Z-score: -2.31
📈 LONG ADA / SHORT SOL (entry signal)

[BTCUSDT - ETHUSDT]
Z-score: 0.17
✅ EXIT position (mean-reversion completed)

🛡️ Safety & Deployment

All credentials are managed via .env and excluded from Git.

Backtesting before deployment is highly recommended.

You can plug this logic into execution systems (e.g., Binance order API) with minimal extension.

🙋 About the Author

Janghyuk Choi — Aspiring quantitative developer and algorithmic trader passionate about applying data science to financial markets. This project was built as part of a trading system engineering portfolio.

For collaboration or questions, contact via GitHub or Telegram.

⭐ Future Improvements

Add dynamic portfolio allocation using Kelly or volatility parity

Enhance cointegration filtering with Hurst exponent or p-value decay

Web dashboard for signal monitoring

Automated order execution engine (Binance Futures)

