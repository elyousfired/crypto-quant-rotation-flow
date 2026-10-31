import React, { useState } from 'react';
import { DefiLlamaData, ProtocolValuation } from '../types';

interface DefiLlamaSubCategoriesProps {
  data: DefiLlamaData;
}

export const DefiLlamaSubCategories: React.FC<DefiLlamaSubCategoriesProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const { rotation_metrics, clusters, comparative_table } = data;

  const fmtUSD = (n?: number) => {
    if (!n || isNaN(n)) return '--';
    if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return '$' + (n / 1e3).toFixed(2) + 'K';
    return '$' + n.toFixed(2);
  };

  const fmtPct = (val?: number) => {
    if (val === undefined || val === null) return '--';
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(2)}%`;
  };

  const filteredProtocols = (comparative_table || []).filter(
    (p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.chain.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      
      {/* Rotation Barometer: Speculative vs Sustainable Yield */}
      <div className="p-5 rounded-xl border border-[#1E2638] bg-[#0E131F]">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
              <h3 className="text-base font-bold font-mono text-white tracking-wide">
                SPECULATIVE VS. SUSTAINABLE YIELD ROTATION BAROMETER
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                DEFILLAMA FLOW ENGINE
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Tracking liquidity migration between speculative venues (DEXes, Perps) and sustainable cashflow infrastructure.
            </p>
          </div>
          <span
            className="px-3 py-1 rounded-md text-xs font-mono font-bold"
            style={{
              backgroundColor: `${rotation_metrics.badge_color}22`,
              color: rotation_metrics.badge_color,
              border: `1px solid ${rotation_metrics.badge_color}44`
            }}
          >
            {rotation_metrics.state_badge}
          </span>
        </div>

        {/* Big Barometer Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
          <div className="p-4 rounded-lg border border-emerald-500/30 bg-emerald-500/5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-emerald-400 tracking-wider uppercase">
                  SUSTAINABLE YIELD & CDP INFRASTRUCTURE
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                  PRODUCTIVE CAPITAL
                </span>
              </div>
              <div className="mt-2 flex items-baseline gap-3">
                <span className="text-2xl font-mono font-bold text-white">
                  {fmtUSD(rotation_metrics.sustainable_yield_tvl)}
                </span>
                <span className="text-sm font-mono font-semibold text-emerald-400">
                  {fmtPct(rotation_metrics.sustainable_yield_7d_change)} (7d)
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Liquid Staking, Restaking, Collateralized Debt (CDP), and Money Markets generating real protocol fees.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-lg border border-purple-500/30 bg-purple-500/5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-purple-400 tracking-wider uppercase">
                  SPECULATIVE TRADING & PERPETUALS
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                  HIGH-BETA LEVERAGE
                </span>
              </div>
              <div className="mt-2 flex items-baseline gap-3">
                <span className="text-2xl font-mono font-bold text-white">
                  {fmtUSD(rotation_metrics.speculative_tvl)}
                </span>
                <span className="text-sm font-mono font-semibold text-purple-400">
                  {fmtPct(rotation_metrics.speculative_7d_change)} (7d)
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                DEX AMMs, Leveraged Derivatives, Options, and speculative liquidity pools.
              </p>
            </div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-[#080A0F] border border-[#1E2638] text-xs font-mono text-gray-300">
          <b>QUANTITATIVE MACRO THESIS:</b> {rotation_metrics.thesis}
        </div>
      </div>

      {/* DefiLlama Clusters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clusters.map((cl, idx) => (
          <div key={idx} className="p-4 rounded-xl border border-[#1E2638] bg-[#0E131F] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold font-mono text-sm text-white">{cl.name}</span>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                    cl.nature === 'SUSTAINABLE_YIELD'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-purple-500/20 text-purple-400'
                  }`}
                >
                  {cl.nature}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-3">{cl.description}</p>
              <div className="text-xl font-bold font-mono text-white mb-1">{fmtUSD(cl.total_tvl)}</div>
              <div
                className={`text-xs font-mono ${
                  cl.avg_7d_change >= 0 ? 'text-emerald-400' : 'text-rose-400'
                } mb-3`}
              >
                7d Weighted Δ: {fmtPct(cl.avg_7d_change)}
              </div>
            </div>
            <div className="pt-2 border-t border-[#1E2638] text-[11px] font-mono text-gray-400 flex justify-between">
              <span>
                Daily Fees: <b className="text-white">{fmtUSD(cl.total_daily_fees)}</b>
              </span>
              <span>
                Daily Rev: <b className="text-cyan-400">{fmtUSD(cl.total_daily_revenue)}</b>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Comparative Valuation Table */}
      <div className="p-5 rounded-xl border border-[#1E2638] bg-[#0E131F]">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-400"></span>
              <h3 className="text-base font-bold font-mono text-white tracking-wide">
                PROTOCOL VALUATION & FUNDAMENTALS (P/E & P/FEES)
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                TOP 50 PROTOCOLS
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Cross-referencing TVL, 24h & Annualized Fees, Revenue, Market Cap, and P/E valuation ratios.
            </p>
          </div>

          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search protocol..."
            className="px-3 py-1.5 rounded-md bg-[#080A0F] border border-[#1E2638] text-xs font-mono text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 w-48"
          />
        </div>

        <div className="overflow-x-auto custom-scrollbar border border-[#1E2638] rounded-lg">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="bg-[#080A0F]/80 text-gray-400 border-b border-[#1E2638] text-[11px]">
                <th className="py-3 px-3">PROTOCOL</th>
                <th className="py-3 px-3">CATEGORY</th>
                <th className="py-3 px-3">CHAIN</th>
                <th className="py-3 px-3 text-right">TVL</th>
                <th className="py-3 px-3 text-right">7D Δ</th>
                <th className="py-3 px-3 text-right">24H FEES</th>
                <th className="py-3 px-3 text-right">ANNUAL REVENUE</th>
                <th className="py-3 px-3 text-right">MCAP</th>
                <th className="py-3 px-3 text-right">P/E RATIO</th>
                <th className="py-3 px-3 text-right">TVL / MCAP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2638]/60 text-gray-300">
              {filteredProtocols.map((p) => {
                const peBadge =
                  p.pe_ratio !== null && p.pe_ratio !== undefined ? (
                    p.pe_ratio < 15 ? (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                        {p.pe_ratio}x (DEEP VALUE)
                      </span>
                    ) : p.pe_ratio < 40 ? (
                      <span className="text-cyan-400">{p.pe_ratio}x</span>
                    ) : (
                      <span className="text-gray-400">{p.pe_ratio}x</span>
                    )
                  ) : (
                    <span className="text-gray-600">--</span>
                  );

                return (
                  <tr key={p.id} className="hover:bg-[#141A29]/60 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-white flex items-center gap-2">
                      {p.logo && <img src={p.logo} alt={p.name} className="w-4 h-4 rounded-full" />}
                      {p.name}
                    </td>
                    <td className="py-2.5 px-3 text-cyan-400">{p.category}</td>
                    <td className="py-2.5 px-3 text-gray-400">{p.chain}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-white">{fmtUSD(p.tvl)}</td>
                    <td
                      className={`py-2.5 px-3 text-right ${
                        (p.change_7d || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {fmtPct(p.change_7d)}
                    </td>
                    <td className="py-2.5 px-3 text-right text-gray-200">{fmtUSD(p.daily_fees)}</td>
                    <td className="py-2.5 px-3 text-right text-gray-200">{fmtUSD(p.annualized_revenue)}</td>
                    <td className="py-2.5 px-3 text-right text-white">{fmtUSD(p.mcap)}</td>
                    <td className="py-2.5 px-3 text-right">{peBadge}</td>
                    <td className="py-2.5 px-3 text-right text-cyan-400">
                      {p.tvl_mcap_ratio ? `${p.tvl_mcap_ratio}x` : '--'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
