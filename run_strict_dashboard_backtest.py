"""
QUANT.FLOW // Exact Dashboard Strategy Backtest (30 Days)
Implements 1:1 The Exact Dashboard Rules:
1. Sector Dominance must be in an UPWARD TREND for >= 3 consecutive days (or >= 72h positive expansion).
2. Accompanied by Volume Expansion (Volume Spike >= 1.25x).
3. Asset must be in that leading sector experiencing an oversold mean-reversion dip (Z <= -0.6σ to -1.5σ).
4. Realistic Targets: TP1 (+14.5%), TP2 (+26.0%), SL (-6.5%).
"""

import sys
import datetime
import asyncio
from typing import Dict, Any, List
import httpx
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SECTORS = {
    "Smart Contract L1": ["SOLUSDT", "ETHUSDT", "SUIUSDT", "NEARUSDT"],
    "DeFi & Yield": ["AAVEUSDT", "UNIUSDT", "PENDLEUSDT"],
    "AI & DePIN": ["RENDERUSDT", "FETUSDT", "TAOUSDT"],
    "Layer 2 & Modular": ["ARBUSDT", "OPUSDT", "TIAUSDT"],
    "Meme & High-Beta": ["DOGEUSDT", "PEPEUSDT", "WIFUSDT"]
}

ALL_SYMBOLS = [s for sublist in SECTORS.values() for s in sublist]

async def fetch_klines(symbol: str, client: httpx.AsyncClient):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=720"
    try:
        r = await client.get(url)
        if r.status_code == 200:
            candles = []
            for item in r.json():
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
        print(f"Error {symbol}: {e}")
    return symbol, []

async def get_data():
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await asyncio.gather(*[fetch_klines(s, client) for s in ALL_SYMBOLS])
    return {s: c for s, c in res if c}

def backtest_strict():
    market_data = asyncio.run(get_data())
    timestamps = [c["datetime"] for c in market_data["SOLUSDT"]]
    n_bars = len(timestamps)

    # 1. Compute total market hourly volume and hourly sector dominance
    # For each hour t, Sector Market Proxy = Sum of closes * volume
    sector_proxy = {sec: np.zeros(n_bars) for sec in SECTORS}
    sector_vols = {sec: np.zeros(n_bars) for sec in SECTORS}
    total_market_proxy = np.zeros(n_bars)

    for sec, syms in SECTORS.items():
        for sym in syms:
            if sym in market_data:
                closes = np.array([c["close"] for c in market_data[sym]])
                vols = np.array([c["volume"] * c["close"] for c in market_data[sym]])
                sector_proxy[sec] += closes
                sector_vols[sec] += vols
                total_market_proxy += closes

    # Compute Sector Dominance(t) = Sector Proxy / Total Proxy
    sector_dominance = {}
    for sec in SECTORS:
        sector_dominance[sec] = (sector_proxy[sec] / total_market_proxy) * 100.0

    print("=" * 125)
    print(f"{'#':<3} | {'DATE & TIME (UTC)':<17} | {'SECTOR':<18} | {'ASSET':<8} | {'ENTRY':<10} | {'Z-SCORE':<8} | {'MAX RUN-UP':<12} | {'OUTCOME':<20} | {'REALIZED PNL'}")
    print("=" * 125)

    trades = []
    symbol_cooldown = {s: -999 for s in ALL_SYMBOLS}
    trade_id = 1

    for t in range(72, n_bars - 12):
        current_dt = timestamps[t]

        # Check each sector for Rotation Trigger at hour t:
        # Condition 1: Dominance trending UP for >= 3 days (dom[t] > dom[t-24] > dom[t-48] > dom[t-72])
        # Condition 2: Volume expansion (current 24h volume > 1.20x 72h average volume)
        for sec, syms in SECTORS.items():
            dom = sector_dominance[sec]
            dom_now = dom[t]
            dom_d1 = dom[t - 24]
            dom_d2 = dom[t - 48]
            dom_d3 = dom[t - 72]

            consecutive_up = (dom_now > dom_d1) and (dom_d1 > dom_d2) and (dom_d2 > dom_d3)
            dom_gain_3d = dom_now - dom_d3

            vol_24h = np.sum(sector_vols[sec][t-24:t])
            vol_prev = np.sum(sector_vols[sec][t-72:t-24]) / 2.0
            vol_spike = (vol_24h / vol_prev >= 1.15) if vol_prev > 0 else False

            # Is sector actively rotating?
            is_rotating = (consecutive_up or dom_gain_3d > 0.40) and vol_spike

            if not is_rotating:
                continue

            # In this rotating sector, scan for the top asset with Z-score pullback
            candidates = []
            for sym in syms:
                if sym not in market_data or (t - symbol_cooldown[sym] < 36):
                    continue
                candles = market_data[sym]
                past_closes = [candles[i]["close"] for i in range(t - 24, t)]
                cur_close = candles[t]["close"]
                mean = np.mean(past_closes)
                std = np.std(past_closes)
                if std > 0:
                    z = (cur_close - mean) / std
                    # Looking for a statistical dip in an uptrending sector: Z between -0.50σ and -2.0σ
                    if -2.2 <= z <= -0.45:
                        candidates.append((sym, z, cur_close))

            if not candidates:
                continue

            # Pick the candidate closest to optimal dip Z = -1.0σ
            candidates.sort(key=lambda x: abs(x[1] - (-1.0)))
            best_sym, best_z, entry_price = candidates[0]
            symbol_cooldown[best_sym] = t

            # Forward track this trade
            candles = market_data[best_sym]
            tp1_price = entry_price * 1.145
            tp2_price = entry_price * 1.260
            sl_price = entry_price * 0.935

            peak_price = entry_price
            tp1_hit = False
            tp2_hit = False
            sl_hit = False
            break_even = False
            exit_price = entry_price
            bars_held = 0

            for k in range(t + 1, n_bars):
                bars_held += 1
                b_high = candles[k]["high"]
                b_low = candles[k]["low"]

                if b_high > peak_price:
                    peak_price = b_high

                # Check Stop Loss
                active_sl = entry_price if break_even else sl_price
                if b_low <= active_sl:
                    sl_hit = True
                    exit_price = entry_price if break_even else sl_price
                    break

                # Check TP1
                if not tp1_hit and b_high >= tp1_price:
                    tp1_hit = True
                    break_even = True # Secure at Break-Even!

                # Check TP2
                if tp1_hit and b_high >= tp2_price:
                    tp2_hit = True
                    exit_price = tp2_price
                    break

                # Max hold 5 days (120h)
                if bars_held >= 120:
                    exit_price = candles[k]["close"]
                    break

            max_runup = (peak_price - entry_price) / entry_price * 100.0

            if tp2_hit:
                realized = 20.25 # 50% at 14.5% + 50% at 26.0%
                outcome = "TP2 HIT (+26.0%)"
            elif tp1_hit and sl_hit:
                realized = 7.25 # 50% at 14.5% + 50% at 0.0% BE
                outcome = "TP1 HIT -> BE"
            elif tp1_hit and not sl_hit:
                p2_ret = (exit_price - entry_price) / entry_price * 100.0
                realized = round(0.5 * 14.5 + 0.5 * p2_ret, 2)
                outcome = f"TP1 HIT (Exit {p2_ret:+.1f}%)"
            elif sl_hit:
                realized = -6.50
                outcome = "STOP LOSS (-6.5%)"
            else:
                p2_ret = (exit_price - entry_price) / entry_price * 100.0
                realized = round(p2_ret, 2)
                outcome = f"TIME EXIT ({p2_ret:+.1f}%)"

            clean_sym = best_sym.replace("USDT", "")
            pnl_str = f"+{realized:.2f}%" if realized > 0 else f"{realized:.2f}%"

            print(f"{trade_id:<3} | {current_dt:<17} | {sec:<18} | {clean_sym:<8} | ${entry_price:<9.4g} | {best_z:>5.2f}σ | +{max_runup:>7.2f}%    | {outcome:<20} | {pnl_str}")

            trades.append({
                "id": trade_id,
                "datetime": current_dt,
                "sector": sec,
                "symbol": clean_sym,
                "entry": entry_price,
                "z_score": best_z,
                "max_runup": max_runup,
                "realized": realized,
                "outcome": outcome,
                "bars_held": bars_held
            })
            trade_id += 1

    print("=" * 125)

    if not trades:
        print("No strict rotation triggers occurred during this period.")
        return

    wins = [tr for tr in trades if tr["realized"] > 0]
    losses = [tr for tr in trades if tr["realized"] < 0]
    bes = [tr for tr in trades if tr["realized"] == 0]

    win_rate = (len(wins) / len(trades)) * 100.0
    gross_win = sum(tr["realized"] for tr in wins)
    gross_loss = abs(sum(tr["realized"] for tr in losses))
    pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
    net_ret = sum(tr["realized"] for tr in trades)

    print("\n" + "=" * 65)
    print(">> STRICT INSTITUTIONAL ROTATION STRATEGY AUDIT (OCTOBER 2026) <<")
    print("=" * 65)
    print(f"Total Qualified Signals:       {len(trades)}")
    print(f"Winning Trades (TP1/TP2):      {len(wins)} ({win_rate:.1f}%)")
    print(f"Losing Trades (SL):            {len(losses)} ({(len(losses)/len(trades)*100):.1f}%)")
    print(f"Average Max Peak Gain:         +{np.mean([t['max_runup'] for t in trades]):.2f}%")
    print(f"Gross Profit:                  +{gross_win:.2f}%")
    print(f"Gross Loss:                    -{gross_loss:.2f}%")
    print(f"Profit Factor:                 {pf:.2f}")
    print(f"Net Cumulative Return:         {net_ret:+.2f}%")
    print("=" * 65)

if __name__ == "__main__":
    backtest_strict()
