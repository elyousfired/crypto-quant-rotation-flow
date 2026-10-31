import React from 'react';
import { RotationSignal } from '../types';

interface RotationSignalCardsProps {
  signals: RotationSignal[];
}

export const RotationSignalCards: React.FC<RotationSignalCardsProps> = ({ signals }) => {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
            <h3 className="text-base font-bold font-mono text-white tracking-wide">
              AUTOMATED ROTATION SIGNALS: Z-SCORE PULLBACK ENTRIES
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              MEAN-REVERSION ENGINE
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Top assets in rotating sectors exhibiting short-term statistical pullbacks (
            <code className="text-cyan-400">Z &lt; -0.2σ</code>) within macro sector uptrends, offering favorable risk/reward.
          </p>
        </div>
        <span className="text-xs font-mono text-gray-400">INSTITUTIONAL QUANT SELECTION</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {signals.map((sig, idx) => {
          const zColor =
            sig.z_score < -1.0 ? 'text-emerald-400' : sig.z_score < 0 ? 'text-cyan-400' : 'text-gray-300';

          return (
            <div
              key={idx}
              className="p-4 rounded-xl border border-[#1E2638] bg-[#0E131F] hover:border-blue-500/50 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    {sig.image && (
                      <img src={sig.image} alt={sig.name} className="w-7 h-7 rounded-full bg-[#080A0F]" />
                    )}
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold font-mono text-sm text-white">{sig.symbol}</span>
                        <span className="text-[10px] font-mono text-gray-400">{sig.name}</span>
                      </div>
                      <span
                        className="text-[10px] font-mono px-1.5 py-0.2 rounded"
                        style={{
                          backgroundColor: `${sig.sector_color}22`,
                          color: sig.sector_color,
                          border: `1px solid ${sig.sector_color}44`
                        }}
                      >
                        {sig.sector}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold font-mono text-white">
                      ${sig.current_price.toLocaleString()}
                    </div>
                    <div
                      className={`text-[10px] font-mono ${
                        sig.price_change_24h >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      24h {sig.price_change_24h >= 0 ? '+' : ''}
                      {sig.price_change_24h.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Quantitative Metric Strip */}
                <div className="grid grid-cols-2 gap-2 my-3 p-2.5 rounded-lg bg-[#080A0F] border border-[#1E2638] text-xs font-mono">
                  <div>
                    <span className="text-[10px] text-gray-400 block">Z-SCORE (24H DIP)</span>
                    <span className={`font-bold ${zColor}`}>{sig.z_score}σ</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-400 block">SECTOR 3D GAIN</span>
                    <span className="font-bold text-emerald-400">+{sig.dominance_gain_3d}%</span>
                  </div>
                </div>

                {/* Execution Levels */}
                <div className="space-y-1.5 text-xs font-mono my-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Entry Zone:</span>
                    <span className="text-cyan-400 font-semibold">{sig.entry_zone}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Take Profit:</span>
                    <span className="text-emerald-400 font-semibold">{sig.take_profit_target}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Invalidation:</span>
                    <span className="text-rose-400 font-semibold">{sig.invalidation_stop}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">R:R Ratio:</span>
                    <span className="text-white font-semibold">{sig.risk_reward_ratio}</span>
                  </div>
                </div>

                <p className="text-[11px] text-gray-400 italic border-t border-[#1E2638] pt-2 mt-2">
                  "{sig.quantitative_rationale}"
                </p>
              </div>

              <div className="mt-4 pt-2 border-t border-[#1E2638] flex items-center justify-between text-[10px] font-mono text-emerald-400">
                <span>HIGH CONVICTION PULLBACK</span>
                <span>READY FOR ENTRY &bull; LIMIT ORDER</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
