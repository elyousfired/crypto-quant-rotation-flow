"""
QUANT.FLOW // Institutional Live Paper Trading Engine
Runs 24/7 Automated Demo Execution on Rotation Signals.
- Enters active rotation pullback signals.
- Automatically executes Take Profit (+14.5% / +26.0%) and Stop Loss (-6.5%).
- Moves Stop Loss to Break-Even upon TP1 hit.
- Permanently stores closed trade history (never deleted).
- Reconstructs and tracks live Cumulative PnL Equity Curve PnL(t).
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("PaperTrader")

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "paper_portfolio.json")

class PaperTrader:
    def __init__(self, data_path: str = DATA_FILE):
        self.data_path = data_path
        self.writable_path = data_path
        if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            self.writable_path = os.path.join("/tmp", "paper_portfolio.json")
        self._ensure_storage()

    def _ensure_storage(self):
        try:
            os.makedirs(os.path.dirname(self.writable_path), exist_ok=True)
            if not os.path.exists(self.writable_path):
                # Copy from seed data_path if available
                if os.path.exists(self.data_path):
                    import shutil
                    try:
                        shutil.copyfile(self.data_path, self.writable_path)
                        return
                    except Exception:
                        pass

            now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            initial_data = {
                "active_trades": [],
                "closed_trades": [],
                "pnl_history": [
                    {"timestamp": now_str, "cumulative_pnl": 0.0, "event": "LIVE_BASELINE_START"}
                ],
                "stats": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "total_realized_pnl": 0.0
                }
            }
            with open(self.writable_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Storage init fallback: {e}")

    def load_portfolio(self) -> Dict[str, Any]:
        for path in (self.writable_path, self.data_path):
            if path and os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading portfolio from {path}: {e}")
        self._ensure_storage()
        if os.path.exists(self.writable_path):
            try:
                with open(self.writable_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"active_trades": [], "closed_trades": [], "pnl_history": [], "stats": {}}

    def save_portfolio(self, data: Dict[str, Any]):
        try:
            with open(self.writable_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save portfolio to {self.writable_path}: {e}")

    def sync_and_evaluate(self, rotation_signals: List[Dict[str, Any]], current_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        1. Auto-enters new rotation signals into active demo trades.
        2. Evaluates active trades against live prices for TP1, TP2, and SL triggers.
        3. Persists results permanently.
        """
        portfolio = self.load_portfolio()
        active_trades = portfolio.get("active_trades", [])
        closed_trades = portfolio.get("closed_trades", [])
        pnl_history = portfolio.get("pnl_history", [])

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        active_symbols = {t["symbol"].upper() for t in active_trades}

        # 1. AUTO-ENTRY: Enter newly identified rotation signals
        for sig in rotation_signals:
            sym = sig.get("symbol", "").upper()
            price = sig.get("current_price", 0.0)

            if not sym or price <= 0:
                continue

            if sym not in active_symbols:
                # Calculate TP & SL thresholds
                tp1 = price * 1.145 # +14.5%
                tp2 = price * 1.260 # +26.0%
                sl = price * 0.935  # -6.5%

                new_trade = {
                    "trade_id": f"TRADE-{sym}-{int(time.time())}",
                    "symbol": sym,
                    "name": sig.get("name", sym),
                    "sector": sig.get("sector", "Other"),
                    "sector_color": sig.get("sector_color", "#3B82F6"),
                    "entry_time": now_str,
                    "entry_price": price,
                    "current_price": price,
                    "unrealized_pnl_pct": 0.0,
                    "max_gain_pct": 0.0,
                    "tp1_price": tp1,
                    "tp2_price": tp2,
                    "sl_price": sl,
                    "active_sl_price": sl,
                    "tp1_hit": False,
                    "status": "ACTIVE"
                }
                active_trades.append(new_trade)
                active_symbols.add(sym)
                logger.info(f"[PAPER TRADER] Auto-entered demo trade on {sym} @ ${price}")

        # Price map helper
        price_lookup = {sig.get("symbol", "").upper(): sig.get("current_price") for sig in rotation_signals}
        if current_prices:
            price_lookup.update(current_prices)

        # 2. EVALUATION: Check TP1, TP2, and SL triggers
        remaining_active = []
        trades_closed_this_round = False

        for tr in active_trades:
            sym = tr["symbol"].upper()
            entry = tr["entry_price"]
            cur_price = price_lookup.get(sym, tr.get("current_price", entry))

            tr["current_price"] = cur_price
            unrealized = ((cur_price - entry) / entry) * 100.0
            tr["unrealized_pnl_pct"] = round(unrealized, 2)

            if unrealized > tr.get("max_gain_pct", 0.0):
                tr["max_gain_pct"] = round(unrealized, 2)

            # Check Stop Loss
            active_sl = tr.get("active_sl_price", tr["sl_price"])
            if cur_price <= active_sl:
                # Stop loss hit
                if tr.get("tp1_hit"):
                    realized = 7.25 # 50% closed at +14.5% earlier, 50% at BE
                    reason = "TP1 HIT (+14.5%) & BE EXIT"
                else:
                    realized = -6.50
                    reason = "STOP LOSS (-6.5%)"

                closed_trade = {
                    "trade_id": tr["trade_id"],
                    "symbol": tr["symbol"],
                    "sector": tr["sector"],
                    "entry_time": tr["entry_time"],
                    "exit_time": now_str,
                    "entry_price": tr["entry_price"],
                    "exit_price": cur_price,
                    "max_gain_pct": tr["max_gain_pct"],
                    "realized_pnl_pct": realized,
                    "exit_reason": reason,
                    "status": "CLOSED"
                }
                closed_trades.append(closed_trade)
                trades_closed_this_round = True
                logger.info(f"[PAPER TRADER] Closed {sym} -> {reason} ({realized:+.2f}%)")
                continue

            # Check TP1
            if not tr.get("tp1_hit") and cur_price >= tr["tp1_price"]:
                tr["tp1_hit"] = True
                tr["active_sl_price"] = entry # Move SL to Break-Even!
                logger.info(f"[PAPER TRADER] {sym} HIT TP1 (+14.5%)! Moving Stop Loss to Break-Even.")

            # Check TP2
            if tr.get("tp1_hit") and cur_price >= tr["tp2_price"]:
                realized = 20.25 # Blended 50% at 14.5% + 50% at 26%
                reason = "TP2 HIT (+26.0%)"
                closed_trade = {
                    "trade_id": tr["trade_id"],
                    "symbol": tr["symbol"],
                    "sector": tr["sector"],
                    "entry_time": tr["entry_time"],
                    "exit_time": now_str,
                    "entry_price": tr["entry_price"],
                    "exit_price": cur_price,
                    "max_gain_pct": tr["max_gain_pct"],
                    "realized_pnl_pct": realized,
                    "exit_reason": reason,
                    "status": "CLOSED"
                }
                closed_trades.append(closed_trade)
                trades_closed_this_round = True
                logger.info(f"[PAPER TRADER] Closed {sym} -> {reason} ({realized:+.2f}%)")
                continue

            remaining_active.append(tr)

        # 3. Update PnL History curve if trades closed
        if trades_closed_this_round or len(pnl_history) <= 1:
            cum_pnl = sum(t["realized_pnl_pct"] for t in closed_trades)
            last_event = closed_trades[-1]["exit_reason"] if closed_trades else "START"
            pnl_history.append({
                "timestamp": now_str,
                "cumulative_pnl": round(cum_pnl, 2),
                "event": f"{closed_trades[-1]['symbol']} {last_event}" if closed_trades else "START"
            })

        # Recalculate statistics
        winning = [t for t in closed_trades if t["realized_pnl_pct"] > 0]
        losing = [t for t in closed_trades if t["realized_pnl_pct"] < 0]
        total_pnl = sum(t["realized_pnl_pct"] for t in closed_trades)
        win_rate = (len(winning) / len(closed_trades) * 100.0) if closed_trades else 0.0

        stats = {
            "total_trades": len(closed_trades),
            "active_trades_count": len(remaining_active),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": round(win_rate, 1),
            "total_realized_pnl": round(total_pnl, 2)
        }

        portfolio["active_trades"] = remaining_active
        portfolio["closed_trades"] = closed_trades
        portfolio["pnl_history"] = pnl_history
        portfolio["stats"] = stats

        self.save_portfolio(portfolio)
        return portfolio
