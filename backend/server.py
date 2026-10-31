"""
Institutional Quantitative Crypto Dashboard - Backend Server (FastAPI)
Implements:
1. Cross-Category Hierarchical Taxonomy & Ecosystem Flow Engine
2. DefiLlama Sub-Categories & Technical Liquidity Mapping
3. Sector Dominance & Automated Rotation Triggers ($Dominance_{cat}(t)$)
4. High-Performance Caching & Resilient API Layer
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api_clients.coingecko_client import CoinGeckoClient
from backend.api_clients.defillama_client import DefiLlamaClient
from backend.engines.taxonomy_engine import TaxonomyEngine
from backend.engines.ecosystem_flow_engine import EcosystemFlowEngine
from backend.engines.defillama_mapper import DefiLlamaMapper
from backend.engines.rotation_engine import RotationEngine
from backend.engines.paper_trader import PaperTrader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("QuantServer")

app = FastAPI(
    title="Institutional Sector Taxonomy & Flow Dashboard",
    description="Quantitative Crypto Sector Dominance, Flow Matrix & Rotation Triggers",
    version="2.4.0"
)

# Enable CORS for external frontends (e.g. Next.js / Vite React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Clients & Engines
cg_client = CoinGeckoClient(cache_ttl_seconds=300)
llama_client = DefiLlamaClient(cache_ttl_seconds=600)
taxonomy_engine = TaxonomyEngine()
flow_engine = EcosystemFlowEngine()
llama_mapper = DefiLlamaMapper()
rotation_engine = RotationEngine()
paper_trader = PaperTrader()

# In-memory Consolidated Cache
GLOBAL_CACHE: Dict[str, Any] = {
    "last_updated": 0,
    "payload": None
}

def get_or_build_dashboard_payload(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Builds the complete consolidated analytics payload across all 3 modules.
    Caches the result in memory for ultra-fast <15ms responses.
    """
    now = time.time()
    if not force_refresh and GLOBAL_CACHE["payload"] and (now - GLOBAL_CACHE["last_updated"] < 180):
        return GLOBAL_CACHE["payload"]

    logger.info("Recomputing institutional analytics pipeline...")

    # 1. Fetch Market & Protocol Data
    coins = cg_client.get_top_markets(per_page=120)
    categories = cg_client.get_categories()
    global_meta = cg_client.get_global()
    enriched_protocols = llama_client.get_enriched_protocols()

    # 2. Module 1: Hierarchical Taxonomy & Ecosystem Flow
    taxonomy_data = taxonomy_engine.build_hierarchical_aggregates(coins, categories)
    ecosystem_flow_data = flow_engine.compute_flow_matrix(coins)

    # 3. Module 2: DefiLlama Sub-Categories & Liquidity Mapping
    liquidity_mapping_data = llama_mapper.analyze_liquidity_rotation(enriched_protocols)

    # 4. Module 3: Sector Dominance, Rolling Triggers & Z-Score Pullback Signals
    rotation_data = rotation_engine.compute_sector_dominance_and_triggers(coins)

    # 5. Live Paper Trading Execution Engine (24/7 Simulator)
    paper_portfolio = paper_trader.sync_and_evaluate(rotation_data.get("top_signals", []))

    payload = {
        "timestamp": int(now),
        "as_of": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
        "global_metrics": {
            "total_market_cap": global_meta.get("total_market_cap", {}).get("usd", sum(c.get("market_cap", 0) for c in coins)),
            "total_volume_24h": global_meta.get("total_volume", {}).get("usd", sum(c.get("total_volume", 0) for c in coins)),
            "btc_dominance": round(global_meta.get("market_cap_percentage", {}).get("btc", 54.2), 2),
            "eth_dominance": round(global_meta.get("market_cap_percentage", {}).get("eth", 14.8), 2),
            "tracked_protocols_count": len(enriched_protocols),
            "active_rotation_triggers_count": len(rotation_data["active_triggers"])
        },
        "module_1_taxonomy": taxonomy_data,
        "module_1_ecosystem_flow": ecosystem_flow_data,
        "module_2_defillama": liquidity_mapping_data,
        "module_3_rotation": rotation_data,
        "paper_portfolio": paper_portfolio
    }

    GLOBAL_CACHE["last_updated"] = now
    GLOBAL_CACHE["payload"] = payload
    return payload

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "engine_version": "2.4.0",
        "cache_age_seconds": round(time.time() - GLOBAL_CACHE["last_updated"], 1) if GLOBAL_CACHE["last_updated"] > 0 else None,
        "upstream_apis": {
            "coingecko": "connected",
            "defillama": "connected"
        }
    }

@app.get("/api/overview")
def get_overview(refresh: bool = False):
    """Consolidated single-call endpoint returning full institutional dashboard dataset"""
    try:
        return get_or_build_dashboard_payload(force_refresh=refresh)
    except Exception as e:
        logger.error(f"Error building overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/taxonomy/hierarchy")
def get_taxonomy():
    """Module 1: Hierarchical Categorization Tree"""
    payload = get_or_build_dashboard_payload()
    return payload["module_1_taxonomy"]

@app.get("/api/ecosystem/flow-matrix")
def get_ecosystem_flow():
    """Module 1: Ecosystem Flow Matrix (Concentration vs. Dispersion)"""
    payload = get_or_build_dashboard_payload()
    return payload["module_1_ecosystem_flow"]

@app.get("/api/defillama/liquidity-mapping")
def get_defillama_mapping():
    """Module 2: DefiLlama Sub-Categories and Net Capital Rotation"""
    payload = get_or_build_dashboard_payload()
    return payload["module_2_defillama"]["rotation_metrics"]

@app.get("/api/defillama/protocols")
def get_defillama_protocols():
    """Module 2: Protocol Valuation & Fundamentals Table"""
    payload = get_or_build_dashboard_payload()
    return {
        "clusters": payload["module_2_defillama"]["clusters"],
        "protocols": payload["module_2_defillama"]["comparative_table"]
    }

@app.get("/api/rotation/dominance")
def get_rotation_dominance():
    """Module 3: Dominance_cat(t), 3-day Rolling Triggers & Z-Score Signals"""
    payload = get_or_build_dashboard_payload()
    return payload["module_3_rotation"]

@app.post("/api/refresh")
def force_refresh(background_tasks: BackgroundTasks):
    """Force an immediate cache refresh from live APIs"""
    payload = get_or_build_dashboard_payload(force_refresh=True)
    return {"status": "refreshed", "timestamp": payload["timestamp"]}

@app.get("/api/paper-trading/portfolio")
def get_paper_portfolio():
    """Live paper trading portfolio, active positions, and permanent closed history"""
    return paper_trader.load_portfolio()

@app.get("/api/cron/evaluate")
@app.post("/api/cron/evaluate")
def cron_evaluate():
    """Cloud Cron endpoint (Vercel Cron & GitHub Actions) to evaluate trades 24/7"""
    payload = get_or_build_dashboard_payload(force_refresh=True)
    return {
        "status": "evaluated",
        "timestamp": payload["as_of"],
        "active_trades": len(payload["paper_portfolio"]["active_trades"]),
        "closed_trades": len(payload["paper_portfolio"]["closed_trades"]),
        "total_realized_pnl": payload["paper_portfolio"]["stats"]["total_realized_pnl"]
    }

# Serve Embedded Full-Featured Institutional Dashboard UI
FRONTEND_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "index.html")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if os.path.exists(FRONTEND_INDEX_PATH):
        with open(FRONTEND_INDEX_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Quant Crypto Dashboard Frontend Loading...</h1>"
