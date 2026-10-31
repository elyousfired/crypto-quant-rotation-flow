import React from 'react';
import { RotationData } from '../types';

interface SectorDominanceChartProps {
  rotationData: RotationData;
}

export const SectorDominanceChart: React.FC<SectorDominanceChartProps> = ({ rotationData }) => {
  const { sectors, active_triggers } = rotationData;

  return (
    <div className="space-y-6">
      
      {/* Active Rotation Trigger Alert Banner */}
      {active_triggers && active_triggers.length > 0 && (
        <div className="p-4 rounded-xl border border-rose-500/40 bg-gradient-to-r from-rose-500/10 via-[#0E131F] to-[#0E131F] relative overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 font-mono text-xl animate-pulse">
                ⚡
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-rose-400 tracking-wider uppercase">
                    ACTIVE ROTATION TRIGGER DETECTED
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/30 text-white font-mono font-semibold">
                    ≥ 3 CONSECUTIVE DAYS UPTREND
                  </span>
                </div>
                <p className="text-sm text-gray-200 mt-0.5">
                  Institutional volume expansion and dominance trend detected across rotating narrative sectors.
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-2">
              {active_triggers.map((trigger, idx) => (
                <div
                  key={idx}
                  className="px-3 py-1.5 rounded-md bg-[#080A0F]/90 border border-rose-500/40 text-xs font-mono flex items-center gap-2"
                >
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: trigger.color }}></span>
                  <span className="font-bold text-white">{trigger.sector}</span>
                  <span className="text-rose-400 font-semibold">
                    {trigger.dom_delta_3d > 0 ? '+' : ''}{trigger.dom_delta_3d}% (3d)
                  </span>
                  <span className="text-gray-400 text-[10px]">VOL {trigger.volume_expansion}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Grid: Dominance Trajectory & Streak Monitor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* 3-Day Rolling Dominance Trajectory Overview */}
        <div className="lg:col-span-2 p-5 rounded-xl border border-[#1E2638] bg-[#0E131F] flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold font-mono tracking-wide text-white">
                    SECTOR DOMINANCE TRAJECTORY ($Dominance_{'{cat}'}(t)$)
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1E2638] text-gray-300">
                    ROLLING 72H WINDOW
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Formula: <code className="text-cyan-400 font-mono">Dominance_cat = Σ MCap_i / Σ MCap_all</code>.
                </p>
              </div>
              <div className="text-[11px] font-mono text-gray-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                HOURLY SPARKLINE COMPOSITE
              </div>
            </div>

            {/* Visual Trajectory Bars Strip */}
            <div className="space-y-3 my-4">
              {sectors.map((sec) => (
                <div key={sec.sector_key} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-gray-300 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: sec.color }}></span>
                      {sec.name}
                    </span>
                    <span className="text-white font-semibold">
                      {sec.current_dominance}%{' '}
                      <span className={sec.dom_delta_3d > 0 ? 'text-emerald-400' : 'text-rose-400'}>
                        ({sec.dom_delta_3d > 0 ? '+' : ''}{sec.dom_delta_3d}% 3d)
                      </span>
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#080A0F] overflow-hidden border border-[#1E2638]">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(sec.current_dominance * 1.5, 100)}%`, backgroundColor: sec.color }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-[#1E2638] flex flex-wrap items-center gap-4 text-xs font-mono">
            {sectors.map((s) => (
              <div key={s.sector_key} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }}></span>
                <span className="text-gray-300">{s.name}:</span>
                <span className="text-white font-bold">{s.current_dominance}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Rotation Streak Monitor List */}
        <div className="p-5 rounded-xl border border-[#1E2638] bg-[#0E131F] flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold font-mono tracking-wide text-white">ROTATION STREAK MONITOR</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1E2638] text-gray-300">
              TREND & VOLUME
            </span>
          </div>
          <p className="text-xs text-gray-400 mb-4">
            Tracking consecutive days of upward dominance expansion coupled with volume surges.
          </p>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[300px] custom-scrollbar pr-1">
            {sectors.map((sec) => {
              const isUp = sec.dom_delta_3d > 0;
              return (
                <div
                  key={sec.sector_key}
                  className={`p-3 rounded-lg border ${
                    sec.is_rotation_triggered ? 'border-rose-500/50 bg-rose-500/5' : 'border-[#1E2638] bg-[#080A0F]/60'
                  } text-xs font-mono`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: sec.color }}></span>
                      <span className="font-semibold text-white">{sec.name}</span>
                    </div>
                    <span className="font-bold text-white">{sec.current_dominance}%</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                    <span>
                      3d Δ: <b className={isUp ? 'text-emerald-400' : 'text-rose-400'}>{isUp ? '+' : ''}{sec.dom_delta_3d}%</b>
                    </span>
                    <span>Streak: <b className="text-white">{sec.consecutive_days_up}d UP</b></span>
                    <span>Vol: <b className="text-cyan-400">{sec.volume_ratio}x</b></span>
                  </div>
                  {sec.is_rotation_triggered && (
                    <div className="mt-2 text-[10px] font-bold text-rose-400 uppercase flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                      ACTIVE ROTATION TRIGGER &bull; VOLUME SURGE
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
};
