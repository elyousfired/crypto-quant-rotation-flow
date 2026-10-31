# QUANT.FLOW // Institutional Crypto Sector Taxonomy & Rotation Dashboard

A high-performance institutional quantitative crypto analytics web application and dashboard. Implements hierarchical cross-category taxonomy, ecosystem liquidity flow matrix (Concentration vs. Dispersion), DefiLlama technical sub-category tracking with valuation multiples (P/E, P/Fees), and automated Sector Rotation Triggers ($Dominance_{cat}(t)$) with Z-Score Pullback entry signals.

---

## 🌟 Core Modules Implemented

### 1. Cross-Category Hierarchical Taxonomy & Ecosystem Flow Engine
- **Hierarchical Categorization Tree**:
  1. **Macro Sector**: Smart Contract Platforms, Decentralized Finance (DeFi), Infrastructure & Interoperability, AI & DePIN, Speculative & Culture.
  2. **Sub-Sector**: Layer 1, Layer 2 & Rollups, Modular DA, Liquid Staking & Restaking, Lending & CDP, AMM & Orderbook DEX, Perpetuals & Derivatives, Yield & Fixed Income, Oracles, Bridges, AI Agents, DePIN, Memes.
  3. **Ecosystem Tag**: Solana Ecosystem, Ethereum Ecosystem, Base Ecosystem, Arbitrum Ecosystem, BNB Chain Ecosystem, Avalanche Ecosystem, Sui Ecosystem.
- **Ecosystem Flow Matrix**:
  - Quantifies liquidity concentration in parent L1/L2 vs dispersal into downstream sub-ecosystem beta tokens.
  - Computes $\Delta_{flow} = \% \Delta MCap_{sub} - \% \Delta MCap_{parent}$, classifying regimes into:
    - **DISPERSION** (Risk-On Beta Dispersal)
    - **CONCENTRATION** (Flight to Parent L1 Quality)
    - **BALANCED** (Parallel Expansion)

### 2. DefiLlama Sub-Categories & Technical Liquidity Mapping
- **Narrative to Financial Sub-Category Mapping**:
  - `Yield & Income` $\to$ Liquid Staking, Restaking, Yield Aggregator, Liquid Restaking.
  - `Lending & Credit` $\to$ CDP, Isolated Lending, Cross-Margin Lending.
  - `Spot Trading & AMMs` $\to$ AMM DEX, DEX Aggregators.
  - `Derivatives & Synthetic Leverage` $\to$ Perpetuals, Options, Leveraged Farming.
  - `RWA` $\to$ Tokenized Treasuries, Private Credit.
- **Capital Rotation Barometer**:
  - Measures net capital flow between Speculative (DEXes, Perps) and Sustainable Yield (Restaking, CDP, Liquid Staking).
- **Comparative Valuation & Fundamentals Table**:
  - Real-time TVL, 7d TVL Change, 24h Fees, 30d Annualized Fees, 24h Revenue, 30d Annualized Revenue, Market Cap, and institutional valuation multiples:
    - **P/E (Price-to-Earnings / MCap / Annualized Revenue)**
    - **P/Fees (MCap / Annualized Fees)**
    - **TVL / MCap Ratio**

### 3. Sector Dominance & Automated Rotation Trigger ($Dominance_{cat}$)
- **Mathematical Formula**:
  $$Dominance_{cat}(t) = \frac{\sum_{i \in cat} MCap_i(t)}{\sum_{all} MCap_{all}(t)}$$
- **Rolling 3-Day Window Tracking**:
  - Real-time composite calculated from hourly sparklines across rolling 72 hours.
- **Rotation Trigger Alert System**:
  - Visually flags any narrative sector trending upward for $\ge 3$ consecutive days accompanied by a Volume Spike ($\ge 1.25\times$ baseline).
- **Automated "Rotation Signal" Cards (Z-Score Pullback Opportunity)**:
  - Computes rolling price Z-Score:
    $$Z = \frac{P_t - \mu_{SMA24}}{\sigma_{24}}$$
  - Identifies top assets in rotating sectors currently in a statistical dip ($Z < -0.15\sigma$), recommending:
    - Target Entry Range (Optimal Dip Buy Zone)
    - Target Take Profit (+14.5% to +26%)
    - Invalidation Stop (-6.5%)
    - Risk/Reward Ratio (e.g. 1 : 3.2)
    - Quantitative Execution Thesis

---

## 🛠️ Architecture & Tech Stack

```
crypto_quant_dashboard/
├── backend/
│   ├── api_clients/
│   │   ├── coingecko_client.py     # Exponential Backoff, Jitter, TTL Cache, 429 Protection
│   │   └── defillama_client.py     # Protocols, Fees, Revenue, Multiples Enrichment
│   ├── engines/
│   │   ├── taxonomy_engine.py      # 3-Tier Categorization Tree & Aggregate Engine
│   │   ├── ecosystem_flow_engine.py# Ecosystem Flow Matrix (Concentration vs Dispersion)
│   │   ├── defillama_mapper.py     # Sub-Category Mapping & Speculative vs Yield Net Flow
│   │   └── rotation_engine.py      # Dominance_cat(t), 3d Triggers, Z-Score Pullback Cards
│   ├── cache/                      # Persistent Disk Cache for instantaneous boot
│   ├── server.py                   # FastAPI REST API & Embedded Web Dashboard
│   └── run.py                      # CLI Verification & Validation Launcher
├── frontend/
│   ├── index.html                  # Sleek Dark-Mode Institutional UI (Tailwind + Chart.js)
│   └── src/
│       ├── components/             # Production React Components
│       │   ├── HeaderMetrics.tsx
│       │   ├── SectorDominanceChart.tsx
│       │   ├── RotationSignalCards.tsx
│       │   ├── EcosystemFlowMatrix.tsx
│       │   ├── DefiLlamaSubCategories.tsx
│       │   └── TaxonomyTree.tsx
│       └── types/
│           └── index.ts            # TypeScript Definitions
├── start_dashboard.py              # Single-Command Launcher
└── README.md
```

---

## 🚀 Quickstart

### 1. Run Pipeline Validation (CLI Test)
```bash
python backend/run.py
```

### 2. Launch Full Web Dashboard & REST API
```bash
python start_dashboard.py
```
- Open your browser at: **`http://localhost:8088`**
- Interactive REST API Docs at: **`http://localhost:8088/docs`**

---

## 📡 REST API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/overview` | `GET` | Consolidated single-trip payload for all 3 modules |
| `/api/taxonomy/hierarchy` | `GET` | 3-tier Macro, Sub-Sector & Token hierarchy |
| `/api/ecosystem/flow-matrix` | `GET` | Ecosystem Flow Matrix (Concentration vs Dispersion) |
| `/api/defillama/liquidity-mapping` | `GET` | Capital rotation between Speculative and Yield |
| `/api/defillama/protocols` | `GET` | Comparative table with TVL, Fees, Revenue & P/E |
| `/api/rotation/dominance` | `GET` | Rolling 3-day Dominance, Active Triggers & Z-Score Signals |
| `/api/refresh` | `POST` | Force immediate cache refresh from live APIs |
| `/api/health` | `GET` | API client connectivity & cache health status |
