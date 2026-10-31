"""
Ecosystem Flow Matrix Engine
Calculates institutional liquidity migration between Parent L1/L2 networks
and their downstream sub-ecosystem tokens (DeFi, Memes, Infrastructure).
Measures Concentration vs. Dispersion regimes in real time.
"""

from typing import Dict, Any, List, Optional
import logging
from backend.engines.taxonomy_engine import ECOSYSTEM_TAGS

logger = logging.getLogger("EcosystemFlowEngine")

class EcosystemFlowEngine:
    def __init__(self):
        self.ecosystems = ECOSYSTEM_TAGS

    def compute_flow_matrix(self, coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Builds the Ecosystem Flow Matrix across all tracked ecosystems.
        Analyzes parent vs. sub-token market cap velocity.
        """
        coin_lookup = {c.get("symbol", "").upper(): c for c in coins}
        matrix_results = []

        for eco_name, eco_def in self.ecosystems.items():
            parent_sym = eco_def["parent_symbol"]
            parent_coin = coin_lookup.get(parent_sym)

            if not parent_coin:
                continue

            parent_mcap = parent_coin.get("market_cap") or 0.0
            parent_vol = parent_coin.get("total_volume") or 0.0
            parent_ch24 = parent_coin.get("price_change_percentage_24h") or 0.0
            parent_ch7d = parent_coin.get("price_change_percentage_7d_in_currency") or 0.0
            parent_price = parent_coin.get("current_price") or 0.0
            parent_img = parent_coin.get("image")

            # Collect sub-ecosystem tokens
            sub_tokens_data = []
            sub_total_mcap = 0.0
            sub_total_vol = 0.0
            weighted_ch24_sum = 0.0
            weighted_ch7d_sum = 0.0

            for sym in eco_def["tokens"]:
                c = coin_lookup.get(sym)
                if c:
                    m = c.get("market_cap") or 0.0
                    v = c.get("total_volume") or 0.0
                    ch24 = c.get("price_change_percentage_24h") or 0.0
                    ch7d = c.get("price_change_percentage_7d_in_currency") or 0.0
                    
                    sub_total_mcap += m
                    sub_total_vol += v
                    weighted_ch24_sum += (ch24 * m)
                    weighted_ch7d_sum += (ch7d * m)

                    sub_tokens_data.append({
                        "symbol": sym,
                        "name": c.get("name"),
                        "price": c.get("current_price"),
                        "mcap": m,
                        "volume_24h": v,
                        "price_change_24h": ch24,
                        "price_change_7d": ch7d,
                        "image": c.get("image")
                    })

            # Calculate volume-weighted sub-ecosystem performance
            sub_avg_ch24 = (weighted_ch24_sum / sub_total_mcap) if sub_total_mcap > 0 else 0.0
            sub_avg_ch7d = (weighted_ch7d_sum / sub_total_mcap) if sub_total_mcap > 0 else 0.0

            total_eco_mcap = parent_mcap + sub_total_mcap
            parent_dominance_ratio = (parent_mcap / total_eco_mcap * 100.0) if total_eco_mcap > 0 else 100.0
            sub_share_ratio = 100.0 - parent_dominance_ratio

            # Relative Momentum Delta (Beta vs Base)
            momentum_delta_24h = sub_avg_ch24 - parent_ch24
            momentum_delta_7d = sub_avg_ch7d - parent_ch7d

            # Regime Determination: Concentration vs Dispersion
            if momentum_delta_24h > 1.8:
                flow_regime = "DISPERSION"
                regime_badge = "Risk-On Beta Dispersal"
                sentiment_color = "#10B981"  # Emerald
                rationale = f"Liquidity is aggressively rotating from {parent_sym} into sub-ecosystem beta tokens (+{momentum_delta_24h:.1f}% relative outperformance)."
                velocity_score = min(100, int(momentum_delta_24h * 15))
            elif momentum_delta_24h < -1.8:
                flow_regime = "CONCENTRATION"
                regime_badge = "L1 Flight to Safety"
                sentiment_color = "#F59E0B"  # Amber
                rationale = f"Capital is contracting back into {parent_sym} safety; sub-ecosystem beta experiencing liquidity drain ({momentum_delta_24h:.1f}% lag)."
                velocity_score = max(-100, int(momentum_delta_24h * 15))
            else:
                flow_regime = "BALANCED"
                regime_badge = "Parallel Expansion"
                sentiment_color = "#06B6D4"  # Cyan
                rationale = f"Parent {parent_sym} and ecosystem tokens are expanding in tandem with synchronized volume."
                velocity_score = int(momentum_delta_24h * 10)

            # Volume Absorption Ratio (Sub-Tokens Volume / Parent Volume)
            vol_absorption_ratio = (sub_total_vol / parent_vol * 100.0) if parent_vol > 0 else 0.0

            matrix_results.append({
                "ecosystem": eco_name,
                "parent_asset": {
                    "symbol": parent_sym,
                    "name": eco_def["parent_name"],
                    "price": parent_price,
                    "mcap": parent_mcap,
                    "volume_24h": parent_vol,
                    "change_24h": parent_ch24,
                    "change_7d": parent_ch7d,
                    "image": parent_img
                },
                "sub_ecosystem": {
                    "total_mcap": round(sub_total_mcap, 2),
                    "total_volume_24h": round(sub_total_vol, 2),
                    "weighted_change_24h": round(sub_avg_ch24, 2),
                    "weighted_change_7d": round(sub_avg_ch7d, 2),
                    "tracked_tokens_count": len(sub_tokens_data),
                    "tokens": sorted(sub_tokens_data, key=lambda x: x["mcap"], reverse=True)
                },
                "flow_metrics": {
                    "total_ecosystem_mcap": round(total_eco_mcap, 2),
                    "parent_dominance_pct": round(parent_dominance_ratio, 2),
                    "sub_share_pct": round(sub_share_ratio, 2),
                    "momentum_delta_24h": round(momentum_delta_24h, 2),
                    "momentum_delta_7d": round(momentum_delta_7d, 2),
                    "vol_absorption_ratio_pct": round(vol_absorption_ratio, 2),
                    "flow_regime": flow_regime,
                    "regime_badge": regime_badge,
                    "sentiment_color": sentiment_color,
                    "velocity_score": velocity_score,
                    "rationale": rationale
                }
            })

        # Sort matrix by total ecosystem market cap
        matrix_results.sort(key=lambda x: x["flow_metrics"]["total_ecosystem_mcap"], reverse=True)
        return matrix_results
