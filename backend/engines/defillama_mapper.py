"""
DefiLlama Sub-Categories & Technical Liquidity Mapping Engine
Maps CoinGecko narrative categories with DefiLlama financial sub-categories.
Tracks capital rotation between Speculative and Sustainable Yield sectors.
Calculates institutional valuation multiples (P/E, P/Fees, TVL/MCap).
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("DefiLlamaMapper")

# Master Narrative to Financial Sub-Category Mapping
NARRATIVE_TO_DEFILLAMA_MAP = {
    "Yield & Income": {
        "description": "Yield-bearing capital, staking derivatives, and vault aggregators",
        "defillama_categories": ["Liquid Staking", "Restaking", "Yield Aggregator", "Yield", "Liquid Restaking", "Basis Trading"],
        "nature": "SUSTAINABLE_YIELD"
    },
    "Lending & Credit": {
        "description": "Collateralized debt protocols, credit markets, and isolated money markets",
        "defillama_categories": ["Lending", "CDP", "Cross Chain Lending", "Undercollateralized Lending"],
        "nature": "SUSTAINABLE_YIELD"
    },
    "Spot Trading & AMMs": {
        "description": "Decentralized automated market makers and spot exchange pools",
        "defillama_categories": ["Dexs", "DEX Aggregator"],
        "nature": "SPECULATIVE"
    },
    "Derivatives & Synthetic Leverage": {
        "description": "Perpetuals, options, and structured synthetic leverage contracts",
        "defillama_categories": ["Derivatives", "Options", "Leveraged Farming", "Synthetics"],
        "nature": "SPECULATIVE"
    },
    "Real World Assets (RWA)": {
        "description": "Tokenized US Treasuries, private credit, and institutional real estate",
        "defillama_categories": ["RWA"],
        "nature": "SUSTAINABLE_YIELD"
    },
    "Bridges & Cross-Chain": {
        "description": "Liquidity networks enabling cross-chain value settlement",
        "defillama_categories": ["Bridge", "Cross Chain"],
        "nature": "INFRASTRUCTURE"
    }
}

class DefiLlamaMapper:
    def __init__(self):
        self.mapping = NARRATIVE_TO_DEFILLAMA_MAP

    def analyze_liquidity_rotation(self, enriched_protocols: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Groups protocols into narrative super-clusters and analyzes
        capital migration between Speculative and Sustainable Yield buckets.
        """
        cluster_stats = {narrative: {
            "name": narrative,
            "description": info["description"],
            "nature": info["nature"],
            "total_tvl": 0.0,
            "protocols_count": 0,
            "weighted_change_7d_sum": 0.0,
            "total_daily_fees": 0.0,
            "total_daily_revenue": 0.0,
            "top_protocols": []
        } for narrative, info in self.mapping.items()}

        speculative_tvl = 0.0
        speculative_7d_sum = 0.0
        yield_tvl = 0.0
        yield_7d_sum = 0.0

        for proto in enriched_protocols:
            cat = proto.get("category", "")
            tvl = proto.get("tvl") or 0.0
            ch7d = proto.get("change_7d") or 0.0
            fees = proto.get("daily_fees") or 0.0
            rev = proto.get("daily_revenue") or 0.0

            matched_narrative = None
            for narrative, info in self.mapping.items():
                if cat in info["defillama_categories"]:
                    matched_narrative = narrative
                    break

            if matched_narrative:
                stat = cluster_stats[matched_narrative]
                stat["total_tvl"] += tvl
                stat["protocols_count"] += 1
                stat["weighted_change_7d_sum"] += (ch7d * tvl)
                stat["total_daily_fees"] += fees
                stat["total_daily_revenue"] += rev
                if len(stat["top_protocols"]) < 6:
                    stat["top_protocols"].append(proto)

                # Bucket aggregation
                if stat["nature"] == "SPECULATIVE":
                    speculative_tvl += tvl
                    speculative_7d_sum += (ch7d * tvl)
                elif stat["nature"] == "SUSTAINABLE_YIELD":
                    yield_tvl += tvl
                    yield_7d_sum += (ch7d * tvl)

        # Calculate weighted 7d performance
        for n, stat in cluster_stats.items():
            tot_tvl = stat["total_tvl"]
            stat["avg_7d_change"] = round((stat["weighted_change_7d_sum"] / tot_tvl), 2) if tot_tvl > 0 else 0.0
            stat["total_tvl"] = round(tot_tvl, 2)
            stat["total_daily_fees"] = round(stat["total_daily_fees"], 2)
            stat["total_daily_revenue"] = round(stat["total_daily_revenue"], 2)

        speculative_avg_7d = round((speculative_7d_sum / speculative_tvl), 2) if speculative_tvl > 0 else 0.0
        yield_avg_7d = round((yield_7d_sum / yield_tvl), 2) if yield_tvl > 0 else 0.0

        # Net Rotation Differential: Yield vs Speculative
        rotation_delta = round(yield_avg_7d - speculative_avg_7d, 2)

        if rotation_delta > 1.5:
            rotation_state = "FLIGHT_TO_YIELD"
            state_label = "Capital Rotating into Sustainable Yield & CDP"
            state_badge = "Yield Accumulation"
            badge_color = "#10B981"
            thesis = f"Institutional capital is derisking out of speculative DEXes/Perps into yield-bearing collateral and CDP debt (+{rotation_delta}% delta)."
        elif rotation_delta < -1.5:
            rotation_state = "RISK_ON_SPECULATION"
            state_label = "Capital Rotating into Speculative DEXes & Derivatives"
            state_badge = "Speculative Expansion"
            badge_color = "#8B5CF6"
            thesis = f"Traders are pulling liquidity from idle staking/CDPs to chase trading volatility and fee revenue on DEXes ({rotation_delta}% delta)."
        else:
            rotation_state = "NEUTRAL_EQUILIBRIUM"
            state_label = "Balanced Liquidity Distribution"
            state_badge = "Equilibrium"
            badge_color = "#06B6D4"
            thesis = "Liquidity growth across trading venues and yield protocols remains balanced with zero distinct macro divergence."

        # Top 50 Protocols for Comparative Table
        table_protocols = enriched_protocols[:50]

        return {
            "rotation_metrics": {
                "rotation_state": rotation_state,
                "state_label": state_label,
                "state_badge": state_badge,
                "badge_color": badge_color,
                "rotation_delta": rotation_delta,
                "thesis": thesis,
                "sustainable_yield_tvl": round(yield_tvl, 2),
                "sustainable_yield_7d_change": yield_avg_7d,
                "speculative_tvl": round(speculative_tvl, 2),
                "speculative_7d_change": speculative_avg_7d
            },
            "clusters": list(cluster_stats.values()),
            "comparative_table": table_protocols
        }
