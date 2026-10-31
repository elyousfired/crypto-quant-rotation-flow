"""
Cross-Category Hierarchical Taxonomy Engine
Builds institutional 3-Tier Categorization Tree:
Macro Sector -> Sub-Sector -> Ecosystem Tag
Maps CoinGecko categories and token markets to the hierarchy.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("TaxonomyEngine")

# Master Hierarchical Taxonomy Definition
TAXONOMY_TREE = {
    "Smart Contract Platforms": {
        "description": "Foundational consensus layers, execution environments, and scaling rollups",
        "sub_sectors": {
            "Layer 1 (L1)": {
                "coingecko_categories": ["layer-1", "smart-contract-platform"],
                "representative_tokens": ["ETH", "SOL", "BNB", "AVAX", "SUI", "NEAR", "ADA", "APT", "DOT", "FTM"],
                "description": "Base consensus blockchains with native execution"
            },
            "Layer 2 & Rollups (L2)": {
                "coingecko_categories": ["layer-2", "arbitrum-ecosystem", "optimism-ecosystem", "base-ecosystem", "polygon-ecosystem"],
                "representative_tokens": ["ARB", "OP", "POL", "MNT", "STRK", "BLAST", "METIS", "ZK"],
                "description": "Execution layers settling on Ethereum or modular data layers"
            },
            "Modular & Data Availability": {
                "coingecko_categories": ["modular-blockchain", "data-availability"],
                "representative_tokens": ["TIA", "DYM", "EIGEN", "SAGA"],
                "description": "Specialized execution, consensus, and DA layers"
            }
        }
    },
    "Decentralized Finance (DeFi)": {
        "description": "Autonomous financial primitives, liquidity pools, and capital markets",
        "sub_sectors": {
            "Liquid Staking & Restaking": {
                "coingecko_categories": ["liquid-staking-tokens", "liquid-restaking-tokens", "restaking"],
                "representative_tokens": ["LDO", "ETHFI", "REZ", "RPL", "JTO", "BB"],
                "description": "Capital-efficient staking and pooled consensus security"
            },
            "Lending & CDP": {
                "coingecko_categories": ["lending", "cdp", "decentralized-derivatives"],
                "representative_tokens": ["AAVE", "MKR", "COMP", "MORPHO", "CRVUSD", "ENA"],
                "description": "Collateralized debt positions, money markets, and synthetic credit"
            },
            "AMM & Orderbook DEX": {
                "coingecko_categories": ["decentralized-exchange", "automated-market-maker-amm"],
                "representative_tokens": ["UNI", "RAY", "JUP", "CRV", "CAKE", "AERO", "ORCA", "DYDX"],
                "description": "Non-custodial spot and swap liquidity infrastructure"
            },
            "Derivatives & Perps": {
                "coingecko_categories": ["perpetuals", "options"],
                "representative_tokens": ["GMX", "DYDX", "SNX", "DRIFT", "GNS", "HYPER"],
                "description": "Decentralized perpetual futures and synthetic leverage protocols"
            },
            "Yield & Fixed Income": {
                "coingecko_categories": ["yield-aggregator", "yield-farming", "fixed-rate-yield"],
                "representative_tokens": ["PENDLE", "YFI", "CVX", "AURA"],
                "description": "Yield tokenization, rate hedging, and auto-compounding"
            }
        }
    },
    "Infrastructure & Interoperability": {
        "description": "Oracles, cross-chain messaging, decentralized storage, and RPC middleware",
        "sub_sectors": {
            "Decentralized Oracles": {
                "coingecko_categories": ["oracle"],
                "representative_tokens": ["LINK", "PYTH", "BAND", "API3"],
                "description": "Off-chain financial data feeds and verifiable random functions"
            },
            "Cross-Chain Bridges & Messaging": {
                "coingecko_categories": ["cross-chain-communication", "bridges"],
                "representative_tokens": ["W", "ZRO", "AXL", "SYN"],
                "description": "State transfer, liquidity bridging, and generalized intent networks"
            },
            "Decentralized Storage & Compute": {
                "coingecko_categories": ["storage"],
                "representative_tokens": ["FIL", "AR", "HNT", "THETA"],
                "description": "Permanent data availability, distributed storage and physical compute"
            }
        }
    },
    "AI & DePIN": {
        "description": "Autonomous AI agent economies, distributed machine learning, and physical hardware networks",
        "sub_sectors": {
            "AI Agents & Frameworks": {
                "coingecko_categories": ["artificial-intelligence", "ai-agents"],
                "representative_tokens": ["FET", "TAO", "RENDER", "VIRTUAL", "AI16Z", "GRASS"],
                "description": "Agentic swarms, decentralized model inference, and decentralized GPU compute"
            },
            "DePIN (Physical Infrastructure)": {
                "coingecko_categories": ["depin"],
                "representative_tokens": ["RNDR", "HNT", "AKT", "MOBILE", "IO", "ATH"],
                "description": "Decentralized wireless, GPU clusters, and sensor networks"
            }
        }
    },
    "Speculative & Culture": {
        "description": "High-beta narrative assets, community tokens, and attention-driven liquidity",
        "sub_sectors": {
            "Meme Assets": {
                "coingecko_categories": ["meme-token"],
                "representative_tokens": ["DOGE", "SHIB", "PEPE", "WIF", "BONK", "FLOKI", "POPCAT", "BRETT", "SPX"],
                "description": "High-velocity narrative and viral attention capital"
            },
            "Gaming & Metaverse": {
                "coingecko_categories": ["gaming", "metaverse"],
                "representative_tokens": ["IMX", "GALA", "BEAM", "AXS", "RON"],
                "description": "Web3 gaming, in-game assets, and virtual economies"
            }
        }
    }
}

# Ecosystem Tags Mapping
ECOSYSTEM_TAGS = {
    "Ethereum Ecosystem": {
        "parent_symbol": "ETH",
        "parent_name": "Ethereum",
        "parent_coingecko_id": "ethereum",
        "tokens": ["LDO", "AAVE", "UNI", "MKR", "PENDLE", "CRV", "ETHFI", "ENS", "RPL", "SNX"]
    },
    "Solana Ecosystem": {
        "parent_symbol": "SOL",
        "parent_name": "Solana",
        "parent_coingecko_id": "solana",
        "tokens": ["RAY", "JUP", "JTO", "PYTH", "WIF", "BONK", "POPCAT", "DRIFT", "ORCA", "RENDER"]
    },
    "Base Ecosystem": {
        "parent_symbol": "ETH",
        "parent_name": "Base Network (Coinbase)",
        "parent_coingecko_id": "ethereum",
        "tokens": ["AERO", "BRETT", "DEGEN", "TOSHI", "VIRTUAL", "SEAM"]
    },
    "Arbitrum Ecosystem": {
        "parent_symbol": "ARB",
        "parent_name": "Arbitrum One",
        "parent_coingecko_id": "arbitrum",
        "tokens": ["GMX", "PENDLE", "RDNT", "MAGIC", "GRAIL", "DPX"]
    },
    "BNB Chain Ecosystem": {
        "parent_symbol": "BNB",
        "parent_name": "BNB Chain",
        "parent_coingecko_id": "binancecoin",
        "tokens": ["CAKE", "XVS", "BAKE", "FLOKI", "THE", "LISTA"]
    },
    "Avalanche Ecosystem": {
        "parent_symbol": "AVAX",
        "parent_name": "Avalanche",
        "parent_coingecko_id": "avalanche-2",
        "tokens": ["JOE", "QI", "COQ", "PNG", "BLS"]
    },
    "Sui Ecosystem": {
        "parent_symbol": "SUI",
        "parent_name": "Sui Network",
        "parent_coingecko_id": "sui",
        "tokens": ["CETUS", "NAVX", "SCA", "DEEP", "BLUB"]
    }
}

class TaxonomyEngine:
    def __init__(self):
        self.tree = TAXONOMY_TREE
        self.ecosystem_tags = ECOSYSTEM_TAGS

    def classify_token(self, symbol: str, name: str = "", cg_categories: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Classifies a token into Macro Sector, Sub-Sector, and Ecosystem Tag.
        """
        sym = (symbol or "").upper().strip()
        cg_cats = [c.lower() for c in (cg_categories or [])]

        macro_res = "Other"
        sub_res = "Unclassified"
        eco_res = "Independent / Multi-Chain"

        # Check ecosystem
        for eco_name, eco_data in self.ecosystem_tags.items():
            if sym == eco_data["parent_symbol"]:
                eco_res = f"Parent L1 ({eco_name})"
                break
            elif sym in eco_data["tokens"]:
                eco_res = eco_name
                break

        # Check taxonomy tree
        found = False
        for macro, macro_info in self.tree.items():
            for sub, sub_info in macro_info["sub_sectors"].items():
                # Direct token match
                if sym in sub_info["representative_tokens"]:
                    macro_res = macro
                    sub_res = sub
                    found = True
                    break
                # Category match
                if any(cat in sub_info["coingecko_categories"] for cat in cg_cats):
                    macro_res = macro
                    sub_res = sub
                    found = True
                    break
            if found:
                break

        # Fallback heuristics for common symbols
        if not found:
            if sym in ["BTC", "WBTC", "DOGE", "LTC"]:
                macro_res = "Smart Contract Platforms"
                sub_res = "Layer 1 (L1)"
            elif "meme" in " ".join(cg_cats) or sym in ["PEPE", "SHIB", "FLOKI", "BONK", "WIF"]:
                macro_res = "Speculative & Culture"
                sub_res = "Meme Assets"
            elif any(w in " ".join(cg_cats) for w in ["defi", "dex", "lending", "yield"]):
                macro_res = "Decentralized Finance (DeFi)"
                sub_res = "AMM & Orderbook DEX"

        return {
            "macro_sector": macro_res,
            "sub_sector": sub_res,
            "ecosystem_tag": eco_res
        }

    def build_hierarchical_aggregates(self, coins: List[Dict[str, Any]], categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates market cap, volume, and performance across Macro and Sub-Sectors.
        """
        category_map = {c.get("id"): c for c in categories}
        macro_stats = {macro: {
            "mcap": 0.0,
            "volume_24h": 0.0,
            "tokens_count": 0,
            "sub_sectors": {sub: {"mcap": 0.0, "volume_24h": 0.0, "tokens": []} for sub in info["sub_sectors"]}
        } for macro, info in self.tree.items()}

        total_tracked_mcap = 0.0

        for coin in coins:
            sym = coin.get("symbol", "").upper()
            mcap = coin.get("market_cap") or 0.0
            vol = coin.get("total_volume") or 0.0
            classification = self.classify_token(sym, coin.get("name", ""))

            macro = classification["macro_sector"]
            sub = classification["sub_sector"]

            if macro in macro_stats and sub in macro_stats[macro]["sub_sectors"]:
                macro_stats[macro]["mcap"] += mcap
                macro_stats[macro]["volume_24h"] += vol
                macro_stats[macro]["tokens_count"] += 1
                
                sub_entry = macro_stats[macro]["sub_sectors"][sub]
                sub_entry["mcap"] += mcap
                sub_entry["volume_24h"] += vol
                sub_entry["tokens"].append({
                    "id": coin.get("id"),
                    "symbol": sym,
                    "name": coin.get("name"),
                    "price": coin.get("current_price"),
                    "mcap": mcap,
                    "price_change_24h": coin.get("price_change_percentage_24h"),
                    "price_change_7d": coin.get("price_change_percentage_7d_in_currency"),
                    "ecosystem": classification["ecosystem_tag"],
                    "image": coin.get("image")
                })
                total_tracked_mcap += mcap

        # Compute dominance shares
        result_tree = []
        for macro, m_data in macro_stats.items():
            mcap = m_data["mcap"]
            macro_dominance = round((mcap / total_tracked_mcap * 100.0), 2) if total_tracked_mcap > 0 else 0.0

            sub_sectors_list = []
            for sub, s_data in m_data["sub_sectors"].items():
                s_mcap = s_data["mcap"]
                sub_dominance = round((s_mcap / mcap * 100.0), 2) if mcap > 0 else 0.0
                
                # Sort tokens by market cap
                sorted_tokens = sorted(s_data["tokens"], key=lambda x: x["mcap"], reverse=True)
                
                sub_sectors_list.append({
                    "name": sub,
                    "market_cap": round(s_mcap, 2),
                    "volume_24h": round(s_data["volume_24h"], 2),
                    "share_of_macro": sub_dominance,
                    "tokens_count": len(sorted_tokens),
                    "top_tokens": sorted_tokens[:6]
                })

            result_tree.append({
                "macro_sector": macro,
                "description": self.tree[macro]["description"],
                "market_cap": round(mcap, 2),
                "volume_24h": round(m_data["volume_24h"], 2),
                "dominance_pct": macro_dominance,
                "sub_sectors": sub_sectors_list
            })

        result_tree.sort(key=lambda x: x["market_cap"], reverse=True)

        return {
            "total_tracked_mcap": round(total_tracked_mcap, 2),
            "macro_sectors": result_tree,
            "taxonomy_definition": self.tree
        }
