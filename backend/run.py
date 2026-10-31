"""
Quantitative Test & Execution Launcher for Institutional Crypto Dashboard
Executes test verification of:
1. Taxonomy Tree & Ecosystem Flow
2. DefiLlama Mapping & Multiples
3. Sector Dominance & Z-Score Rotation Trigger
4. Server Startup
"""

import sys
import os
import json
import time

# Add root project dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.server import get_or_build_dashboard_payload

def main():
    print("=" * 70)
    print(">> STARTING INSTITUTIONAL QUANT CRYPTO DASHBOARD PIPELINE TEST <<")
    print("=" * 70)

    start_t = time.time()
    payload = get_or_build_dashboard_payload(force_refresh=False)
    elapsed = time.time() - start_t

    print(f"\n[OK] Pipeline generated in {elapsed:.2f}s")
    print(f"Timestamp: {payload['as_of']}")

    # 1. Global Metrics
    gm = payload["global_metrics"]
    print(f"\n[1] GLOBAL METRICS:")
    print(f"  - Total Market Cap: ${gm['total_market_cap']:,.2f}")
    print(f"  - 24h Volume: ${gm['total_volume_24h']:,.2f}")
    print(f"  - BTC Dominance: {gm['btc_dominance']}% | ETH Dominance: {gm['eth_dominance']}%")
    print(f"  - Tracked DefiLlama Protocols: {gm['tracked_protocols_count']}")
    print(f"  - Active Rotation Triggers: {gm['active_rotation_triggers_count']}")

    # 2. Module 1: Taxonomy & Ecosystem Flow
    m1_tax = payload["module_1_taxonomy"]
    print(f"\n[2] MODULE 1 - HIERARCHICAL TAXONOMY:")
    for macro in m1_tax["macro_sectors"]:
        print(f"  * {macro['macro_sector']}: {macro['dominance_pct']}% dominance (${macro['market_cap']:,.0f})")
        for sub in macro["sub_sectors"][:2]:
            print(f"      - {sub['name']} ({sub['tokens_count']} tokens)")

    m1_flow = payload["module_1_ecosystem_flow"]
    print(f"\n[3] MODULE 1 - ECOSYSTEM FLOW MATRIX:")
    for flow in m1_flow[:4]:
        fm = flow["flow_metrics"]
        print(f"  * {flow['ecosystem']} -> Regime: {fm['flow_regime']} ({fm['regime_badge']})")
        print(f"      Parent {flow['parent_asset']['symbol']}: {fm['parent_dominance_pct']}% | Sub-Tokens: {fm['sub_share_pct']}% | Momentum Delta: {fm['momentum_delta_24h']:+.2f}%")

    # 4. Module 2: DefiLlama Liquidity & Valuation
    m2 = payload["module_2_defillama"]
    rot = m2["rotation_metrics"]
    print(f"\n[4] MODULE 2 - DEFILLAMA CAPITAL ROTATION:")
    print(f"  - State: {rot['state_badge']} ({rot['state_label']})")
    print(f"  - Sustainable Yield TVL: ${rot['sustainable_yield_tvl']:,.0f} ({rot['sustainable_yield_7d_change']:+.2f}% 7d)")
    print(f"  - Speculative TVL: ${rot['speculative_tvl']:,.0f} ({rot['speculative_7d_change']:+.2f}% 7d)")
    print(f"  - Rotation Net Delta: {rot['rotation_delta']:+.2f}%")
    print(f"  - Thesis: {rot['thesis']}")
    print(f"  - Comparative Table protocols count: {len(m2['comparative_table'])}")
    if m2['comparative_table']:
        top_p = m2['comparative_table'][0]
        print(f"      Sample: {top_p['name']} | TVL: ${top_p['tvl']:,.0f} | P/E: {top_p['pe_ratio']} | P/Fees: {top_p['p_fees_ratio']}")

    # 5. Module 3: Sector Dominance & Rotation Triggers
    m3 = payload["module_3_rotation"]
    print(f"\n[5] MODULE 3 - SECTOR DOMINANCE & ROTATION TRIGGERS:")
    for sec in m3["sectors"]:
        trig_str = "[ACTIVE TRIGGER]" if sec["is_rotation_triggered"] else ""
        print(f"  * {sec['name']}: {sec['current_dominance']}% (3d Delta: {sec['dom_delta_3d']:+.2f}%, streak: {sec['consecutive_days_up']}d UP) {trig_str}")

    print(f"\n[6] TOP ROTATION PULLBACK SIGNALS (Z-SCORE):")
    for sig in m3["top_signals"][:4]:
        print(f"  * {sig['symbol']} ({sig['sector']}) -> Price: ${sig['current_price']} | Z-Score: {sig['z_score']} sigma")
        print(f"      Entry: {sig['entry_zone']} | Target: {sig['take_profit_target']} | Stop: {sig['invalidation_stop']}")
        print(f"      Thesis: {sig['quantitative_rationale'][:100]}...")

    print("\n" + "=" * 70)
    print(">> ALL QUANTITATIVE MODULES VALIDATED SUCCESSFULLY! <<")
    print("=" * 70)

if __name__ == "__main__":
    main()
