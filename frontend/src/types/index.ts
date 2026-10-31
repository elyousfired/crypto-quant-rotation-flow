/**
 * Institutional Quantitative Crypto Dashboard - TypeScript Type Definitions
 */

export interface GlobalMetrics {
  total_market_cap: number;
  total_volume_24h: number;
  btc_dominance: number;
  eth_dominance: number;
  tracked_protocols_count: number;
  active_rotation_triggers_count: number;
}

export interface TrackedToken {
  id: string;
  symbol: string;
  name: string;
  price: number;
  mcap: number;
  volume_24h?: number;
  price_change_24h: number;
  price_change_7d?: number;
  ecosystem?: string;
  image?: string;
}

export interface SubSector {
  name: string;
  market_cap: number;
  volume_24h: number;
  share_of_macro: number;
  tokens_count: number;
  top_tokens: TrackedToken[];
}

export interface MacroSector {
  macro_sector: string;
  description: string;
  market_cap: number;
  volume_24h: number;
  dominance_pct: number;
  sub_sectors: SubSector[];
}

export interface TaxonomyData {
  total_tracked_mcap: number;
  macro_sectors: MacroSector[];
  taxonomy_definition: Record<string, any>;
}

export interface ParentAsset {
  symbol: string;
  name: string;
  price: number;
  mcap: number;
  volume_24h: number;
  change_24h: number;
  change_7d: number;
  image?: string;
}

export interface FlowMetrics {
  total_ecosystem_mcap: number;
  parent_dominance_pct: number;
  sub_share_pct: number;
  momentum_delta_24h: number;
  momentum_delta_7d: number;
  vol_absorption_ratio_pct: number;
  flow_regime: 'DISPERSION' | 'CONCENTRATION' | 'BALANCED';
  regime_badge: string;
  sentiment_color: string;
  velocity_score: number;
  rationale: string;
}

export interface EcosystemFlowItem {
  ecosystem: string;
  parent_asset: ParentAsset;
  sub_ecosystem: {
    total_mcap: number;
    total_volume_24h: number;
    weighted_change_24h: number;
    weighted_change_7d: number;
    tracked_tokens_count: number;
    tokens: TrackedToken[];
  };
  flow_metrics: FlowMetrics;
}

export interface ProtocolValuation {
  id: string;
  name: string;
  symbol: string;
  category: string;
  chain: string;
  chains: string[];
  tvl: number;
  change_1d?: number;
  change_7d?: number;
  mcap?: number;
  daily_fees?: number;
  annualized_fees?: number;
  daily_revenue?: number;
  annualized_revenue?: number;
  pe_ratio?: number;
  p_fees_ratio?: number;
  tvl_mcap_ratio?: number;
  logo?: string;
}

export interface DefiLlamaCluster {
  name: string;
  description: string;
  nature: 'SUSTAINABLE_YIELD' | 'SPECULATIVE' | 'INFRASTRUCTURE';
  total_tvl: number;
  protocols_count: number;
  avg_7d_change: number;
  total_daily_fees: number;
  total_daily_revenue: number;
  top_protocols: ProtocolValuation[];
}

export interface DefiLlamaData {
  rotation_metrics: {
    rotation_state: string;
    state_label: string;
    state_badge: string;
    badge_color: string;
    rotation_delta: number;
    thesis: string;
    sustainable_yield_tvl: number;
    sustainable_yield_7d_change: number;
    speculative_tvl: number;
    speculative_7d_change: number;
  };
  clusters: DefiLlamaCluster[];
  comparative_table: ProtocolValuation[];
}

export interface SectorSnapshot {
  sector_key: string;
  name: string;
  color: string;
  current_dominance: number;
  market_cap: number;
  volume_24h: number;
  dom_delta_24h: number;
  dom_delta_3d: number;
  volume_ratio: number;
  trend_trajectory: number[];
  consecutive_days_up: number;
  is_rotation_triggered: boolean;
  tracked_tokens: string[];
}

export interface RotationTrigger {
  sector: string;
  color: string;
  current_dominance: number;
  dom_delta_3d: number;
  volume_expansion: string;
  streak_days: number;
  status: string;
  signal_timestamp: string;
}

export interface RotationSignal {
  symbol: string;
  name: string;
  image?: string;
  sector: string;
  sector_color: string;
  current_price: number;
  z_score: number;
  price_change_24h: number;
  price_change_7d: number;
  dominance_gain_3d: number;
  entry_zone: string;
  take_profit_target: string;
  invalidation_stop: string;
  risk_reward_ratio: string;
  signal_type: string;
  quantitative_rationale: string;
}

export interface RotationData {
  sectors: SectorSnapshot[];
  active_triggers: RotationTrigger[];
  top_signals: RotationSignal[];
}

export interface DashboardPayload {
  timestamp: number;
  as_of: string;
  global_metrics: GlobalMetrics;
  module_1_taxonomy: TaxonomyData;
  module_1_ecosystem_flow: EcosystemFlowItem[];
  module_2_defillama: DefiLlamaData;
  module_3_rotation: RotationData;
}
