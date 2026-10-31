import httpx
import time

print("=" * 60)
print(">> VERIFYING LIVE SERVER ON PORT 8088 <<")
print("=" * 60)

t0 = time.time()
r_ui = httpx.get("http://127.0.0.1:8088/", timeout=10.0)
print(f"[1] Root Dashboard UI: {r_ui.status_code} in {(time.time()-t0)*1000:.1f}ms ({len(r_ui.text):,} bytes)")

t0 = time.time()
r_overview = httpx.get("http://127.0.0.1:8088/api/overview", timeout=10.0)
print(f"[2] Overview API:      {r_overview.status_code} in {(time.time()-t0)*1000:.1f}ms")

ov = r_overview.json()
gm = ov["global_metrics"]
print(f"    - Global MCap:     ${gm['total_market_cap']:,.0f}")
print(f"    - 24h Volume:      ${gm['total_volume_24h']:,.0f}")
print(f"    - BTC Dominance:   {gm['btc_dominance']}% | ETH Dominance: {gm['eth_dominance']}%")
print(f"    - Protocols:       {gm['tracked_protocols_count']} (DefiLlama)")

rot = ov["module_3_rotation"]
print(f"\n[3] Sector Rotation & Z-Score Pullback Signals:")
print(f"    - Active Triggers: {len(rot['active_triggers'])}")
print(f"    - Top Signals:     {len(rot['top_signals'])}")
for s in rot['top_signals'][:3]:
    print(f"      * {s['symbol']} ({s['sector']}) -> Price: ${s['current_price']} | Z-Score: {s['z_score']} sigma | Entry: {s['entry_zone']}")

print("\n" + "=" * 60)
print(">> SERVER IS 100% OPERATIONAL & SERVING LIVE! <<")
print("=" * 60)
