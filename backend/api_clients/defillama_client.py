"""
Institutional Quantitative DefiLlama API Client
Fetches TVL protocols, financial sub-categories, fees, and revenue data.
Provides disk caching and memory indexing for low-latency queries (<10ms).
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DefiLlamaClient")

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class DefiLlamaClient:
    BASE_URL = "https://api.llama.fi"

    def __init__(self, cache_ttl_seconds: int = 600):
        self.cache_ttl = cache_ttl_seconds
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "InstitutionalQuantTerminal/2.4 (DefiLlama-Client)"
        }

    def _get_cache_filepath(self, name: str) -> str:
        return os.path.join(CACHE_DIR, f"llama_{name}.json")

    def _read_cache(self, key: str) -> Optional[Any]:
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]

        disk_path = self._get_cache_filepath(key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                    if time.time() - entry.get("timestamp", 0) < self.cache_ttl:
                        self.memory_cache[key] = entry
                        return entry["data"]
            except Exception as e:
                logger.warning(f"Error reading disk cache {disk_path}: {e}")
        return None

    def _write_cache(self, key: str, data: Any):
        entry = {"timestamp": time.time(), "data": data}
        self.memory_cache[key] = entry
        disk_path = self._get_cache_filepath(key)
        try:
            with open(disk_path, "w", encoding="utf-8") as f:
                json.dump(entry, f)
        except Exception as e:
            logger.warning(f"Error writing cache {disk_path}: {e}")

    def get_protocols(self) -> List[Dict[str, Any]]:
        """Fetch all TVL protocols from DefiLlama"""
        cached = self._read_cache("protocols")
        if cached:
            return cached

        url = f"{self.BASE_URL}/protocols"
        logger.info("Fetching DefiLlama /protocols...")
        try:
            with httpx.Client(timeout=20.0) as client:
                resp = client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    self._write_cache("protocols", data)
                    return data
        except Exception as e:
            logger.error(f"Failed to fetch DefiLlama /protocols: {e}")

        # Fallback to stale disk cache if any
        disk_path = self._get_cache_filepath("protocols")
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("data", [])
            except Exception:
                pass
        return []

    def get_fees_and_revenue(self) -> Dict[str, Any]:
        """Fetch daily fees and revenue for all protocols"""
        cached = self._read_cache("fees_revenue")
        if cached:
            return cached

        url = f"{self.BASE_URL}/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
        logger.info("Fetching DefiLlama /overview/fees...")
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    self._write_cache("fees_revenue", data)
                    return data
        except Exception as e:
            logger.error(f"Failed to fetch DefiLlama /overview/fees: {e}")

        disk_path = self._get_cache_filepath("fees_revenue")
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("data", {})
            except Exception:
                pass
        return {}

    def get_enriched_protocols(self) -> List[Dict[str, Any]]:
        """
        Merge protocols TVL with fee/revenue metrics and calculate
        annualized multiples (P/E, P/Fees, TVL/MCap).
        """
        protocols = self.get_protocols()
        fees_data = self.get_fees_and_revenue()

        # Build fee lookup map by protocol name & slug
        fee_map = {}
        for p in fees_data.get("protocols", []):
            name = (p.get("name") or "").lower().strip()
            defillama_id = p.get("defillamaId")
            slug = (p.get("module") or "").lower().strip()
            entry = {
                "dailyFees": p.get("dailyFees"),
                "dailyRevenue": p.get("dailyRevenue"),
                "total24h": p.get("total24h"),
                "change_1d": p.get("change_1d")
            }
            if name:
                fee_map[name] = entry
            if slug:
                fee_map[slug] = entry
            if defillama_id:
                fee_map[str(defillama_id)] = entry

        enriched = []
        for p in protocols:
            tvl = p.get("tvl") or 0
            if tvl <= 0:
                continue

            name = p.get("name", "")
            name_lower = name.lower().strip()
            slug_lower = (p.get("slug") or "").lower().strip()
            fee_info = fee_map.get(name_lower) or fee_map.get(slug_lower) or {}

            daily_fees = fee_info.get("dailyFees") or 0.0
            daily_revenue = fee_info.get("dailyRevenue") or 0.0
            annualized_fees = daily_fees * 365.0 if daily_fees > 0 else None
            annualized_revenue = daily_revenue * 365.0 if daily_revenue > 0 else None

            mcap = p.get("mcap")
            pe_ratio = None
            p_fees_ratio = None
            tvl_mcap_ratio = None

            if mcap and mcap > 0:
                if annualized_revenue and annualized_revenue > 0:
                    pe_ratio = round(mcap / annualized_revenue, 2)
                if annualized_fees and annualized_fees > 0:
                    p_fees_ratio = round(mcap / annualized_fees, 2)
                tvl_mcap_ratio = round(tvl / mcap, 2)

            enriched.append({
                "id": p.get("id"),
                "name": name,
                "symbol": p.get("symbol", ""),
                "category": p.get("category", "Other"),
                "chain": p.get("chain", "Multi-Chain"),
                "chains": p.get("chains", []),
                "tvl": round(tvl, 2),
                "change_1d": p.get("change_1d"),
                "change_7d": p.get("change_7d"),
                "mcap": round(mcap, 2) if mcap else None,
                "daily_fees": round(daily_fees, 2) if daily_fees else None,
                "annualized_fees": round(annualized_fees, 2) if annualized_fees else None,
                "daily_revenue": round(daily_revenue, 2) if daily_revenue else None,
                "annualized_revenue": round(annualized_revenue, 2) if annualized_revenue else None,
                "pe_ratio": pe_ratio,
                "p_fees_ratio": p_fees_ratio,
                "tvl_mcap_ratio": tvl_mcap_ratio,
                "logo": p.get("logo")
            })

        # Sort by TVL descending
        enriched.sort(key=lambda x: x["tvl"], reverse=True)
        return enriched
