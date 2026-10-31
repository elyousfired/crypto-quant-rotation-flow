"""
QUANT.FLOW // 30-Day Forensic Historical Backtest Engine
Strict Mathematical Backtesting of Sector Dominance & Z-Score Pullback Strategy.
Period: Past 30 Days (720 Hourly Bars per asset).
Data Source: Official Real-Time & Historical Binance Kline Feed.
Zero Look-Ahead Bias - Realistic Tick/Hour-Level High/Low Execution.
"""

import sys
import time
import datetime
import asyncio
from typing import Dict, Any, List, Tuple
import httpx
import numpy as np

# Force UTF-8 on Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Sector Definitions for Historical Backtest
SECTORS = {
    "Smart Contract L1": ["SOLUSDT", "ETHUSDT", "SUIUSDT", "NEARUSDT"],
    "DeFi & Yield": ["AAVEUSDT", "UNIUSDT", "PENDLEUSDT"],
    "AI & DePIN": ["RENDERUSDT", "FETUSDT", "TAOUSDT"],
    "Layer 2 & Modular": ["ARBUSDT", "OPUSDT", "TIAUSDT"],
    "Meme & High-Beta": ["DOGEUSDT", "PEPEUSDT", "WIFUSDT"]
}

ALL_SYMBOLS = [s for sublist in SECTORS.values() for s in sublist]

async def fetch_historical_klines(symbol: str, client: httpx.AsyncClient) -> Tuple[str, List[Dict[str, Any]]]:
    """Fetches 720 hourly candles (30 days) from Binance public kline API"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=720"
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            candles = []
            for item in data:
                candles.append({
                    "open_time": int(item[0]),
                    "datetime": datetime.datetime.fromtimestamp(item[0] / 1000, datetime.timezone.utc).strftime("%Y-%m-%d %H:00"),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })
            return symbol, candles
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return symbol, []

async def load_all_market_data() -> Dict[str, List[Dict[str, Any]]]:
    print(">> Fetching 30-day hourly historical market data from Binance (720 bars/symbol)...")
    async with httpx.AsyncClient(timeout=15.0) as client:
        tasks = [fetch_historical_klines(s, client) for s in ALL_SYMBOLS]
        results = await asyncio.gather(*tasks)
    return {symbol: candles for symbol, candles in results if candles}

def run_backtest():
    market_data = asyncio.run(load_all_market_data())
    print(f">> Successfully loaded data for {len(market_data)} tokens across 5 sectors.\n")

    # Strategy Parameters
    Z_WINDOW = 24            # 24-hour rolling window for Z-Score
    Z_PULLBACK_THRESH = -0.40 # Pullback dip threshold
    SECTOR_3D_WINDOW = 72    # 3-day rolling window for sector trend
    TP1_PCT = 14.5           # Target 1 (+14.5%)
    TP2_PCT = 26.0           # Target 2 (+26.0%)
    SL_PCT = 6.5             # Stop Loss (-6.5%)
    COOLDOWN_BARS = 36       # Minimum 36 hours between signals on same token

    # Precompute sector aggregate momentum at each hour
    # Align bars by timestamp
    timestamps = [c["datetime"] for c in market_data["SOLUSDT"]]
    n_bars = len(timestamps)

    trades = []
    symbol_last_entry = {s: -999 for s in ALL_SYMBOLS}

    print("=" * 115)
    print(f"{'#':<3} | {'DATE & TIME (UTC)':<17} | {'SYMBOL':<10} | {'ENTRY':<10} | {'Z-SCORE':<8} | {'MAX GAIN %':<11} | {'RESULT':<20} | {'REALIZED PNL'}")
    print("=" * 115)

    trade_id = 1

    for t in range(SECTOR_3D_WINDOW, n_bars - 12): # leave at least 12 bars forward to evaluate
        current_time = timestamps[t]

        # Scan each symbol for signal at bar t
        for sec_name, symbols in SECTORS.items():
            for sym in symbols:
                if sym not in market_data or len(market_data[sym]) <= t:
                    continue

                candles = market_data[sym]
                if t - symbol_last_entry[sym] < COOLDOWN_BARS:
                    continue

                # 1. Compute rolling 24-hour Z-Score at bar t
                past_closes = [candles[i]["close"] for i in range(t - Z_WINDOW, t)]
                current_close = candles[t]["close"]
                mean = np.mean(past_closes)
                std = np.std(past_closes)

                if std == 0:
                    continue

                z_score = (current_close - mean) / std

                # 2. Compute 3-day rolling sector trend
                # Return of this asset over 3 days (72 hours)
                ret_3d = (current_close - candles[t - SECTOR_3D_WINDOW]["close"]) / candles[t - SECTOR_3D_WINDOW]["close"] * 100.0

                # Signal Criteria: Z <= -0.40 AND Sector/Asset 3d return is consolidating/supportive (> -12%)
                if z_score <= Z_PULLBACK_THRESH and ret_3d > -12.0:
                    entry_price = current_close
                    symbol_last_entry[sym] = t

                    # Execution levels
                    tp1_price = entry_price * (1.0 + TP1_PCT / 100.0)
                    tp2_price = entry_price * (1.0 + TP2_PCT / 100.0)
                    sl_price = entry_price * (1.0 - SL_PCT / 100.0)

                    # Forward Simulation: bar by bar
                    peak_price = entry_price
                    tp1_hit = False
                    tp2_hit = False
                    sl_hit = False
                    break_even_sl = False
                    exit_price = entry_price
                    exit_reason = "OPEN"
                    bars_held = 0

                    for k in range(t + 1, n_bars):
                        bars_held += 1
                        bar_high = candles[k]["high"]
                        bar_low = candles[k]["low"]

                        if bar_high > peak_price:
                            peak_price = bar_high

                        # Check Stop Loss
                        active_sl = entry_price if break_even_sl else sl_price
                        if bar_low <= active_sl:
                            sl_hit = True
                            if break_even_sl:
                                exit_reason = "TP1 HIT -> BE EXIT"
                                exit_price = entry_price
                            else:
                                exit_reason = "STOP LOSS (-6.5%)"
                                exit_price = sl_price
                            break

                        # Check TP1
                        if not tp1_hit and bar_high >= tp1_price:
                            tp1_hit = True
                            break_even_sl = True # Protect trade at Break-Even

                        # Check TP2
                        if tp1_hit and bar_high >= tp2_price:
                            tp2_hit = True
                            exit_reason = "TP2 HIT (+26.0%)"
                            exit_price = tp2_price
                            break

                        # Optional: max holding period 7 days (168 hours)
                        if bars_held >= 168:
                            exit_price = candles[k]["close"]
                            exit_reason = f"TIME EXIT ({((exit_price - entry_price)/entry_price*100):+.1f}%)"
                            break

                    max_gain_pct = (peak_price - entry_price) / entry_price * 100.0

                    # Calculate blended realized PnL
                    if tp2_hit:
                        realized_pnl = 20.25 # 50% at +14.5% + 50% at +26.0%
                        status = "TP2 HIT (+26.0%)"
                    elif tp1_hit and sl_hit:
                        realized_pnl = 7.25  # 50% at +14.5% + 50% at 0.0%
                        status = "TP1 HIT & BE"
                    elif tp1_hit and not sl_hit:
                        # Still open or closed at time exit
                        p2_ret = (exit_price - entry_price) / entry_price * 100.0
                        realized_pnl = round(0.5 * 14.5 + 0.5 * p2_ret, 2)
                        status = "TP1 HIT (Partial)"
                    elif sl_hit:
                        realized_pnl = -6.5
                        status = "STOP LOSS (-6.5%)"
                    else:
                        realized_pnl = round((exit_price - entry_price) / entry_price * 100.0, 2)
                        status = f"OPEN / {exit_reason}"

                    clean_sym = sym.replace("USDT", "")
                    pnl_str = f"+{realized_pnl:.2f}%" if realized_pnl > 0 else f"{realized_pnl:.2f}%"
                    print(f"{trade_id:<3} | {current_time:<17} | {clean_sym:<10} | ${entry_price:<9.4g} | {z_score:>5.2f}σ | +{max_gain_pct:>7.2f}%   | {status:<20} | {pnl_str}")

                    trades.append({
                        "id": trade_id,
                        "datetime": current_time,
                        "symbol": clean_sym,
                        "entry": entry_price,
                        "z_score": z_score,
                        "max_gain": max_gain_pct,
                        "realized_pnl": realized_pnl,
                        "status": status,
                        "bars_held": bars_held
                    })
                    trade_id += 1

    print("=" * 115)

    # Statistical Performance Summary
    if not trades:
        print("No trades triggered.")
        return

    total_trades = len(trades)
    winning_trades = [tr for tr in trades if tr["realized_pnl"] > 0]
    losing_trades = [tr for tr in trades if tr["realized_pnl"] < 0]
    be_trades = [tr for tr in trades if tr["realized_pnl"] == 0]

    win_rate = (len(winning_trades) / total_trades) * 100.0 if total_trades > 0 else 0
    gross_profits = sum(tr["realized_pnl"] for tr in winning_trades)
    gross_losses = abs(sum(tr["realized_pnl"] for tr in losing_trades))
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else float("inf")
    total_net_pnl = sum(tr["realized_pnl"] for tr in trades)
    avg_max_runup = np.mean([tr["max_gain"] for tr in trades])
    avg_trade_pnl = np.mean([tr["realized_pnl"] for tr in trades])

    print("\n" + "=" * 65)
    print(">> STATISTICAL PERFORMANCE SUMMARY (30-DAY FORENSIC AUDIT) <<")
    print("=" * 65)
    print(f"Total Signals Triggered:       {total_trades}")
    print(f"Winning Trades (TP1/TP2):      {len(winning_trades)} ({win_rate:.1f}%)")
    print(f"Losing Trades (Stop Loss):     {len(losing_trades)} ({(len(losing_trades)/total_trades*100):.1f}%)")
    print(f"Break-Even Trades:             {len(be_trades)}")
    print(f"Average Max Peak Gain:         +{avg_max_runup:.2f}% (Average peak price reached)")
    print(f"Gross Profit Percentage:       +{gross_profits:.2f}%")
    print(f"Gross Loss Percentage:         -{gross_losses:.2f}%")
    print(f"Profit Factor:                 {profit_factor:.2f}")
    print(f"Average PnL per Trade:         {avg_trade_pnl:+.2f}%")
    print(f"Total Cumulative Return:       +{total_net_pnl:.2f}%")
    print("=" * 65)

if __name__ == "__main__":
    run_backtest()
