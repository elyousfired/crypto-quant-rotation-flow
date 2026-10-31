import React from 'react';
import { EcosystemFlowItem } from '../types';

interface EcosystemFlowMatrixProps {
  flowMatrix: EcosystemFlowItem[];
}

export const EcosystemFlowMatrix: React.FC<EcosystemFlowMatrixProps> = ({ flowMatrix }) => {
  const fmtPct = (val: number) => {
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(2)}%`;
  };

  return (
    <div className="p-5 rounded-xl border border-[#1E2638] bg-[#0E131F]">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-400"></span>
            <h3 className="text-base font-bold font-mono text-white tracking-wide">
              ECOSYSTEM FLOW MATRIX: CONCENTRATION VS. DISPERSION
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              CAPITAL VELOCITY RATIO
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Calculates whether capital is concentrating in the parent L1/L2 network or dispersing into downstream sub-ecosystem beta tokens.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Dispersal (Beta Outperforming)
          </span>
          <span className="flex items-center gap-1 text-amber-400">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span> Concentration (L1 Outperforming)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {flowMatrix.map((item, idx) => {
          const p = item.parent_asset;
          const sub = item.sub_ecosystem;
          const fm = item.flow_metrics;

          return (
            <div
              key={idx}
              className="p-4 rounded-xl border border-[#1E2638] bg-[#0E131F] hover:border-blue-500/40 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {p.image && <img src={p.image} alt={p.symbol} className="w-6 h-6 rounded-full" />}
                    <div>
                      <h4 className="font-mono font-bold text-sm text-white">{item.ecosystem}</h4>
                      <span className="text-[10px] font-mono text-gray-400">
                        Parent: {p.symbol} (${p.price.toLocaleString()})
                      </span>
                    </div>
                  </div>
                  <span
                    className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold"
                    style={{
                      backgroundColor: `${fm.sentiment_color}22`,
                      color: fm.sentiment_color,
                      border: `1px solid ${fm.sentiment_color}44`
                    }}
                  >
                    {fm.regime_badge}
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="my-3 space-y-1">
                  <div className="flex justify-between text-[11px] font-mono text-gray-400">
                    <span>
                      Parent L1 Share: <b className="text-white">{fm.parent_dominance_pct}%</b>
                    </span>
                    <span>
                      Sub-Beta Share: <b className="text-cyan-400">{fm.sub_share_pct}%</b>
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#080A0F] overflow-hidden flex border border-[#1E2638]">
                    <div className="h-full bg-blue-500" style={{ width: `${fm.parent_dominance_pct}%` }}></div>
                    <div className="h-full bg-emerald-500" style={{ width: `${fm.sub_share_pct}%` }}></div>
                  </div>
                </div>

                {/* Velocity Stats */}
                <div className="grid grid-cols-2 gap-2 p-2.5 rounded-lg bg-[#080A0F] border border-[#1E2638] text-xs font-mono my-3">
                  <div>
                    <span className="text-[10px] text-gray-400 block">{p.symbol} 24H CHG</span>
                    <span className={`font-bold ${p.change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {fmtPct(p.change_24h)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-400 block">SUB-TOKENS AVG</span>
                    <span
                      className={`font-bold ${
                        sub.weighted_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {fmtPct(sub.weighted_change_24h)}
                    </span>
                  </div>
                </div>

                <div className="flex justify-between text-xs font-mono text-gray-300 my-2">
                  <span className="text-gray-400">Momentum Delta:</span>
                  <span
                    className={`font-bold ${
                      fm.momentum_delta_24h >= 0 ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    {fm.momentum_delta_24h >= 0 ? '+' : ''}
                    {fm.momentum_delta_24h}% (24h)
                  </span>
                </div>

                <p className="text-[11px] text-gray-400 italic mt-2 border-t border-[#1E2638] pt-2">
                  {fm.rationale}
                </p>
              </div>

              {/* Sub-Tokens Chips */}
              <div className="mt-4 pt-3 border-t border-[#1E2638]">
                <span className="text-[10px] font-mono text-gray-400 uppercase block mb-1.5">
                  Top Tracked Beta Assets:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {(sub.tokens || []).slice(0, 5).map((tok, tIdx) => (
                    <span
                      key={tIdx}
                      className="px-2 py-0.5 rounded bg-[#080A0F] border border-[#1E2638] text-[10px] font-mono text-gray-200 flex items-center gap-1"
                    >
                      <b>{tok.symbol}</b>
                      <span className={tok.price_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                        {fmtPct(tok.price_change_24h)}
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
