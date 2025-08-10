
import argparse, os
import pandas as pd
import numpy as np

def load_data(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df

def strategy_sma(df, fast=10, slow=20):
    df = df.copy()
    df["SMA_fast"] = df["Close"].rolling(fast).mean()
    df["SMA_slow"] = df["Close"].rolling(slow).mean()
    df["signal"] = np.where(df["SMA_fast"] > df["SMA_slow"], 1, 0)
    return df

def strategy_momentum(df, lookback=10):
    df = df.copy()
    df["signal"] = np.where(df["Close"] > df["Close"].shift(lookback), 1, 0)
    return df

def strategy_meanrev(df, lookback=5, z=1.0):
    df = df.copy()
    df["ret"] = df["Close"].pct_change()
    mu = df["ret"].rolling(lookback).mean()
    sd = df["ret"].rolling(lookback).std()
    zscore = (df["ret"] - mu) / (sd + 1e-9)
    df["signal"] = np.where(zscore < -z, 1, np.where(zscore > z, -1, 0))
    return df

def strategy_breakout(df, lookback=20):
    df = df.copy()
    df["hh"] = df["High"].rolling(lookback).max()
    df["ll"] = df["Low"].rolling(lookback).min()
    df["signal"] = np.where(df["Close"] > df["hh"].shift(1), 1,
                            np.where(df["Close"] < df["ll"].shift(1), -1, 0))
    return df

def backtest(df, signal_col="signal"):
    df = df.copy()
    df["ret"] = df["Close"].pct_change().fillna(0)
    df["strat_ret"] = df[signal_col].shift(1).fillna(0) * df["ret"]
    df["equity"] = (1 + df["strat_ret"]).cumprod()
    # Metrics
    total_ret = df["equity"].iloc[-1] - 1
    cagr = (df["equity"].iloc[-1]) ** (252/len(df)) - 1 if len(df)>0 else 0
    drawdown = (df["equity"] / df["equity"].cummax() - 1).min()
    sharpe = (df["strat_ret"].mean() / (df["strat_ret"].std() + 1e-9)) * np.sqrt(252)
    return df, {"TotalReturn": float(total_ret), "CAGR": float(cagr), "MaxDrawdown": float(drawdown), "Sharpe": float(sharpe)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--strategy", choices=["sma","momentum","meanrev","breakout"], default="sma")
    ap.add_argument("--sma_fast", type=int, default=10)
    ap.add_argument("--sma_slow", type=int, default=20)
    ap.add_argument("--momentum_lb", type=int, default=10)
    ap.add_argument("--meanrev_lb", type=int, default=5)
    ap.add_argument("--meanrev_z", type=float, default=1.0)
    ap.add_argument("--breakout_lb", type=int, default=20)
    args = ap.parse_args()

    df = load_data(args.data)
    if args.strategy == "sma":
        df = strategy_sma(df, fast=args.sma_fast, slow=args.sma_slow)
    elif args.strategy == "momentum":
        df = strategy_momentum(df, lookback=args.momentum_lb)
    elif args.strategy == "meanrev":
        df = strategy_meanrev(df, lookback=args.meanrev_lb, z=args.meanrev_z)
    else:
        df = strategy_breakout(df, lookback=args.breakout_lb)

    out_df, metrics = backtest(df)
    os.makedirs("out", exist_ok=True)
    out_df.to_csv("out/equity.csv", index=False)
    print("Metrics:", metrics)

if __name__ == "__main__":
    main()
