"""
QUANT.FLOW // Cloud 24/7 Evaluator
Runs on GitHub Actions / Cloud Cron to evaluate active demo trades even when PC is OFF.
Fetches real-time prices from Binance public API and updates paper_portfolio.json.
"""

import sys
import os
import json
import httpx
import logging

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from backend.engines.paper_trader import PaperTrader
from backend.api_clients.coingecko_client import CoinGeckoClient
from backend.engines.rotation_engine import RotationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CloudPaperTrader")

def evaluate_cloud():
    logger.info(">> Starting 24/7 Cloud Demo Evaluation...")
    trader = PaperTrader()
    portfolio = trader.load_portfolio()
    active_trades = portfolio.get("active_trades", [])

    # 1. Fetch live prices for active positions
    price_map = {}
    with httpx.Client(timeout=10.0) as client:
        for tr in active_trades:
            sym = tr["symbol"].upper()
            binance_pair = f"{sym}USDT"
            try:
                # Try Binance ticker first (fastest)
                r = client.get(f"https://api.binance.com/api/v3/ticker/price?symbol={binance_pair}")
                if r.status_code == 200:
                    price_map[sym] = float(r.json()["price"])
                    logger.info(f"Live Price {sym}: ${price_map[sym]}")
            except Exception as e:
                logger.warning(f"Could not fetch Binance price for {sym}: {e}")

    # 2. Check for new signals via CoinGecko + RotationEngine
    try:
        cg = CoinGeckoClient(cache_ttl_seconds=60)
        coins = cg.get_top_markets(per_page=100)
        rot_engine = RotationEngine()
        rot_data = rot_engine.compute_sector_dominance_and_triggers(coins)
        top_signals = rot_data.get("top_signals", [])
    except Exception as e:
        logger.warning(f"Error fetching new rotation signals: {e}")
        top_signals = []

    # 3. Sync and evaluate active positions
    updated_portfolio = trader.sync_and_evaluate(top_signals, current_prices=price_map)

    stats = updated_portfolio.get("stats", {})
    logger.info(f"Cloud Eval Complete: Active: {len(updated_portfolio.get('active_trades', []))}, Closed: {len(updated_portfolio.get('closed_trades', []))}, Total Realized PnL: {stats.get('total_realized_pnl')}%")

if __name__ == "__main__":
    evaluate_cloud()
