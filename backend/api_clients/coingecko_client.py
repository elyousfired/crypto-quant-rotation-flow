"""
Institutional Quantitative CoinGecko API Client
Provides resilient data fetching with Exponential Backoff, Jitter,
Memory TTL Caching, and Disk Persistence to protect against 429 Rate Limits.
"""

import os
import json
import time
import random
import logging
from typing import Dict, Any, List, Optional
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CoinGeckoClient")

if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    CACHE_DIR = "/tmp/quant_cache"
else:
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    CACHE_DIR = "/tmp/quant_cache"
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception:
        pass

class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = cache_ttl_seconds
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "InstitutionalQuantTerminal/2.4 (DefiLlama-CoinGecko-Rotation)"
        }

    def _get_cache_filepath(self, cache_key: str) -> str:
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in cache_key)
        return os.path.join(CACHE_DIR, f"cg_{safe_key}.json")

    def _read_cache(self, cache_key: str) -> Optional[Any]:
        # 1. Check memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]

        # 2. Check disk cache
        disk_path = self._get_cache_filepath(cache_key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                    # If within TTL, use it and update memory cache
                    if time.time() - entry.get("timestamp", 0) < self.cache_ttl:
                        self.memory_cache[cache_key] = entry
                        return entry["data"]
            except Exception as e:
                logger.warning(f"Error reading disk cache {disk_path}: {e}")

        return None

    def _write_cache(self, cache_key: str, data: Any):
        entry = {
            "timestamp": time.time(),
            "data": data
        }
        self.memory_cache[cache_key] = entry
        disk_path = self._get_cache_filepath(cache_key)
        try:
            with open(disk_path, "w", encoding="utf-8") as f:
                json.dump(entry, f)
        except Exception as e:
            logger.warning(f"Error writing disk cache {disk_path}: {e}")

    def _read_stale_cache(self, cache_key: str) -> Optional[Any]:
        """Returns any available disk/memory cache regardless of expiration (fallback for 429)"""
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]["data"]
        disk_path = self._get_cache_filepath(cache_key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                    return entry.get("data")
            except Exception:
                pass
        return None

    def _request_with_backoff(self, endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Any:
        cache_key = f"{endpoint}_{json.dumps(params or {}, sort_keys=True)}"
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        url = f"{self.BASE_URL}{endpoint}"
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching CoinGecko {endpoint} (Attempt {attempt + 1}/{max_retries})...")
                with httpx.Client(timeout=12.0) as client:
                    resp = client.get(url, params=params, headers=self.headers)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        self._write_cache(cache_key, data)
                        return data
                    elif resp.status_code == 429:
                        wait_sec = (1.5 * (2 ** attempt)) + random.uniform(0.5, 1.5)
                        logger.warning(f"CoinGecko Rate Limit (429). Backing off for {wait_sec:.2f}s...")
                        time.sleep(wait_sec)
                    else:
                        logger.warning(f"CoinGecko HTTP {resp.status_code}: {resp.text[:120]}")
                        time.sleep(1.0)
            except Exception as e:
                last_error = e
                logger.warning(f"Request exception on {endpoint}: {e}")
                time.sleep(1.0)

        # Fallback to stale cache if API failed / 429
        stale = self._read_stale_cache(cache_key)
        if stale is not None:
            logger.info(f"Returning stale cache fallback for {endpoint}")
            return stale

        logger.error(f"Failed to fetch {endpoint} and no cache available. Last error: {last_error}")
        return None

    def get_categories(self) -> List[Dict[str, Any]]:
        """Fetch CoinGecko Categories list with market cap and volume data"""
        data = self._request_with_backoff("/coins/categories")
        if data:
            return data
        return []

    def get_top_markets(self, per_page: int = 150, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch top coins by market cap with 168-hour sparklines for Z-score and rotation analysis"""
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "true",
            "price_change_percentage": "24h,7d"
        }
        data = self._request_with_backoff("/coins/markets", params=params)
        if data:
            return data
        return []

    def get_global(self) -> Dict[str, Any]:
        """Fetch global crypto market metrics"""
        data = self._request_with_backoff("/global")
        if data and "data" in data:
            return data["data"]
        return {}
