# Quant Strategy Backtester
**Academic/Personal Portfolio Demonstration** — This repository showcases applied skills for hiring review. 
It is designed to be **fully runnable offline** from the README and **not** presented as a production system.

**Repo:** https://github.com/Charlemon23/quant-strategy-backtester


# Quant Strategy Backtester 📊

Run SMA, Momentum, Mean Reversion, and Breakout strategies on price data.
Ships with sample data and produces performance metrics + equity curve.

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python backtest.py --data data/sample/AAPL_sample.csv --strategy sma --sma_fast 5 --sma_slow 10
```

Outputs equity curve to `out/equity.csv` and prints metrics.
