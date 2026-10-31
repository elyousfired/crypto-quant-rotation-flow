import React from 'react';
import { TaxonomyData } from '../types';

interface TaxonomyTreeProps {
  data: TaxonomyData;
}

export const TaxonomyTree: React.FC<TaxonomyTreeProps> = ({ data }) => {
  const fmtUSD = (n: number) => {
    if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T';
    if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B';
    return '$' + (n / 1e6).toFixed(2) + 'M';
  };

  return (
    <div className="p-5 rounded-xl border border-[#1E2638] bg-[#0E131F]">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-400"></span>
            <h3 className="text-base font-bold font-mono text-white tracking-wide">
              3-TIER HIERARCHICAL CATEGORIZATION TREE
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">
              MACRO &bull; SUB-SECTOR &bull; ECOSYSTEM
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Cross-category asset grouping mapped from CoinGecko categories and real-time market valuations.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {data.macro_sectors.map((macro, idx) => (
          <div key={idx} className="border border-[#1E2638] rounded-xl bg-[#0E131F] overflow-hidden">
            {/* Macro Header */}
            <div className="p-4 bg-[#141A29]/50 flex flex-wrap items-center justify-between gap-3 border-b border-[#1E2638]">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-mono font-bold text-sm text-white">{macro.macro_sector}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-semibold">
                    {macro.dominance_pct}% TOTAL SHARE
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-0.5">{macro.description}</p>
              </div>
              <div className="text-right text-xs font-mono">
                <span className="text-gray-400 text-[10px] block">SECTOR MCAP</span>
                <span className="font-bold text-white">{fmtUSD(macro.market_cap)}</span>
              </div>
            </div>

            {/* Sub-Sectors Grid */}
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {macro.sub_sectors.map((sub, sIdx) => (
                <div
                  key={sIdx}
                  className="p-3 rounded-lg bg-[#080A0F] border border-[#1E2638] text-xs font-mono flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-cyan-400">{sub.name}</span>
                      <span className="text-[10px] text-gray-400">{sub.share_of_macro}% of macro</span>
                    </div>
                    <div className="text-sm font-bold text-white mb-2">{fmtUSD(sub.market_cap)}</div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {sub.top_tokens.map((t, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-1.5 py-0.5 rounded bg-[#0E131F] border border-[#1E2638] text-[10px] font-mono text-gray-300"
                      >
                        {t.symbol}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
