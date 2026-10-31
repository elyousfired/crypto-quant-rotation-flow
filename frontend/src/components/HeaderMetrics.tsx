import React from 'react';
import { GlobalMetrics } from '../types';

interface HeaderMetricsProps {
  metrics: GlobalMetrics;
  onRefresh: () => void;
  isSyncing: boolean;
  lastSyncTime?: string;
}

export const HeaderMetrics: React.FC<HeaderMetricsProps> = ({
  metrics,
  onRefresh,
  isSyncing,
  lastSyncTime
}) => {
  const fmtUSD = (n: number) => {
    if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T';
    if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B';
    return '$' + (n / 1e6).toFixed(2) + 'M';
  };

  return (
    <header className="border-b border-[#1E2638] bg-[#0E131F]/95 backdrop-blur sticky top-0 z-50 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        
        {/* Brand Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 via-cyan-400 to-emerald-400 flex items-center justify-center font-mono font-bold text-black text-sm shadow-lg shadow-blue-500/20">
            QF
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold tracking-wider font-mono text-white">QUANT.FLOW</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-semibold">
                INSTITUTIONAL v2.4
              </span>
              <span className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                LIVE FEED
              </span>
            </div>
            <p className="text-[11px] text-gray-400">Hierarchical Taxonomy &bull; DefiLlama Liquidity &bull; Automated Rotation Triggers</p>
          </div>
        </div>

        {/* Global Quant Metrics Strip */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="hidden md:flex flex-col border-l border-[#1E2638] pl-3">
            <span className="text-gray-400 text-[10px]">TOTAL CRYPTO MCAP</span>
            <span className="text-white font-semibold">{fmtUSD(metrics.total_market_cap)}</span>
          </div>
          <div className="hidden md:flex flex-col border-l border-[#1E2638] pl-3">
            <span className="text-gray-400 text-[10px]">24H VOLUME</span>
            <span className="text-white font-semibold">{fmtUSD(metrics.total_volume_24h)}</span>
          </div>
          <div className="flex flex-col border-l border-[#1E2638] pl-3">
            <span className="text-gray-400 text-[10px]">BTC / ETH DOM</span>
            <span className="text-white font-semibold">
              {metrics.btc_dominance}% / <span className="text-cyan-400">{metrics.eth_dominance}%</span>
            </span>
          </div>
          <div className="flex flex-col border-l border-[#1E2638] pl-3">
            <span className="text-gray-400 text-[10px]">ACTIVE TRIGGERS</span>
            <span className="text-rose-400 font-bold flex items-center gap-1">
              <span className={`w-1.5 h-1.5 rounded-full ${metrics.active_rotation_triggers_count > 0 ? 'bg-rose-500 animate-ping' : 'bg-gray-500'}`}></span>
              {metrics.active_rotation_triggers_count} ALERTS
            </span>
          </div>
        </div>

        {/* Sync Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            disabled={isSyncing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#141A29] hover:bg-[#1E2638] text-xs font-mono text-gray-200 border border-[#1E2638] transition-all"
          >
            <span className={isSyncing ? 'animate-spin' : ''}>🔄</span>
            <span>{isSyncing ? 'SYNCING...' : 'SYNC'}</span>
          </button>
          {lastSyncTime && (
            <span className="text-[10px] text-gray-500 font-mono hidden sm:inline">{lastSyncTime}</span>
          )}
        </div>

      </div>
    </header>
  );
};
