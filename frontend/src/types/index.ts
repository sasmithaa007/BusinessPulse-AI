// ─── Authentication ────────────────────────────────────────────────────────────

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'analyst' | 'viewer';
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterResponse {
  id: number;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

// ─── Business Scenario ────────────────────────────────────────────────────────

export type BusinessScenario = 'fintech' | 'saas' | 'developer_tools';

// ─── Customer ─────────────────────────────────────────────────────────────────

export interface Customer {
  id: number;
  customer_code: string;
  name: string;
  email: string;
  customer_type: 'individual' | 'business' | 'enterprise';
  business_scenario: BusinessScenario;
  signup_date: string;
  country: string;
  status: 'active' | 'inactive' | 'churned' | 'suspended';
  segment: 'champion' | 'loyal' | 'at_risk' | 'new' | 'hibernating' | 'lost' | string;
  lifetime_value: number;
  churn_risk_score: number;
  transactions_count?: number;
  last_activity?: string;
}

// ─── Transaction ──────────────────────────────────────────────────────────────

export interface Transaction {
  id: number;
  customer_id: number;
  transaction_code: string;
  transaction_date: string;
  amount: number;
  currency: string;
  status: 'completed' | 'failed' | 'pending' | 'refunded' | 'cancelled';
  payment_method: string;
  failure_reason: string | null;
  gateway: string;
  processing_time_ms: number;
  business_scenario: BusinessScenario;
  customer_name?: string;
}

// ─── Subscription ─────────────────────────────────────────────────────────────

export interface Subscription {
  id: number;
  customer_id: number;
  plan_name: string;
  monthly_amount: number;
  subscription_status: 'active' | 'cancelled' | 'paused' | 'trial' | 'expired';
  start_date: string;
  end_date?: string | null;
  trial_end_date?: string | null;
  next_billing_date?: string | null;
  customer_name?: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface DashboardKPI {
  label: string;
  value: string | number;
  change: number;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: string;
  format: 'number' | 'currency' | 'percentage';
  description?: string;
}

export interface DashboardSummary {
  total_revenue: number;
  total_customers: number;
  active_customers: number;
  total_transactions: number;
  revenue_change: number;
  customer_change: number;
  transaction_change: number;
  avg_transaction_value: number;
  mrr?: number;
  arr?: number;
  churn_rate?: number;
  nrr?: number;
}

// ─── Chart Data ───────────────────────────────────────────────────────────────

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number | boolean | null | undefined;
}

export interface RevenueTrendPoint {
  month: string;
  revenue: number;
  transactions: number;
  avg_transaction?: number;
}

export interface CustomerTrendPoint {
  month: string;
  new_customers: number;
  churned_customers: number;
  active_customers: number;
  net_growth: number;
}

// ─── Revenue ──────────────────────────────────────────────────────────────────

export interface RevenueSummary {
  total_revenue: number;
  successful_revenue: number;
  failed_revenue: number;
  refunded_revenue: number;
  avg_transaction_value: number;
  revenue_this_month: number;
  revenue_last_month: number;
  mom_growth: number;
  mrr?: number;
  arr?: number;
  nrr?: number;
  expansion_mrr?: number;
  churned_mrr?: number;
}

export interface RevenueLeakageItem {
  category: string;
  amount: number;
  percentage: number;
  description: string;
}

// ─── Transactions ─────────────────────────────────────────────────────────────

export interface TransactionSummary {
  total_transactions: number;
  completed_transactions: number;
  failed_transactions: number;
  pending_transactions: number;
  refunded_transactions: number;
  total_volume: number;
  success_rate: number;
  failure_rate: number;
  avg_processing_time_ms: number;
}

export interface TransactionFailure {
  reason: string;
  count: number;
  amount_lost: number;
  percentage: number;
}

// ─── Churn & Retention ────────────────────────────────────────────────────────

export interface ChurnStats {
  total_churned: number;
  churn_rate: number;
  avg_churn_risk_score: number;
  high_risk_customers: number;
  medium_risk_customers: number;
  low_risk_customers: number;
  revenue_at_risk: number;
  churn_by_segment?: Record<string, number>;
  churn_reasons?: Array<{ reason: string; count: number; percentage: number }>;
}

export interface ChurnTrendPoint {
  month: string;
  churned: number;
  churn_rate: number;
  at_risk: number;
}

export interface RetentionStats {
  overall_retention_rate: number;
  net_revenue_retention: number;
  gross_revenue_retention: number;
  avg_customer_lifetime_months: number;
  avg_lifetime_value: number;
  expansion_revenue: number;
  contraction_revenue: number;
}

export interface CohortRetentionRow {
  cohort: string;
  size: number;
  months: (number | null)[];
}

// ─── Segments & RFM ──────────────────────────────────────────────────────────

export interface SegmentDistribution {
  segment: string;
  count: number;
  percentage: number;
  revenue_share: number;
  avg_lifetime_value: number;
  color?: string;
}

export interface RFMSegment {
  segment: string;
  count: number;
  avg_recency: number;
  avg_frequency: number;
  avg_monetary: number;
  total_revenue: number;
  percentage: number;
}

// ─── Insights ─────────────────────────────────────────────────────────────────

export interface InsightItem {
  id: string;
  business_problem: string;
  metric: string;
  observed_value: string;
  threshold: string;
  explanation: string;
  recommended_action: string;
  priority: 'high' | 'medium' | 'low';
  evidence_level: 'confirmed' | 'correlation' | 'hypothesis';
  impact_estimate?: string;
  affected_customers?: number;
  potential_revenue?: number;
}

// ─── Performance / Operations ─────────────────────────────────────────────────

export interface PerformanceSummary {
  avg_processing_time_ms: number;
  p50_processing_time_ms: number;
  p95_processing_time_ms: number;
  p99_processing_time_ms: number;
  slow_transactions_count: number;
  slow_transactions_percentage: number;
  gateway_performance: Array<{
    gateway: string;
    avg_ms: number;
    success_rate: number;
    transaction_count: number;
  }>;
}

export interface OperationsSummary {
  api_success_rate: number;
  avg_api_response_ms: number;
  failed_webhooks: number;
  retry_rate: number;
  error_rate: number;
  uptime_percentage: number;
}

// ─── Feature Adoption ─────────────────────────────────────────────────────────

export interface FeatureAdoption {
  feature_name: string;
  adoption_rate: number;
  active_users: number;
  total_users: number;
  trend: 'up' | 'down' | 'stable';
  change: number;
}

// ─── Datasets ─────────────────────────────────────────────────────────────────

export interface Dataset {
  id: number;
  name: string;
  filename: string;
  file_size: number;
  row_count: number;
  columns: string[];
  status: 'processing' | 'ready' | 'error';
  created_at: string;
  updated_at: string;
  error_message?: string | null;
}

export interface DatasetPreview {
  columns: string[];
  rows: Record<string, string | number | boolean | null>[];
  total_rows: number;
  preview_rows: number;
}

// ─── Pagination & API ─────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface ApiError {
  message: string;
  details?: string | Record<string, string[]>;
  status_code?: number;
}

// ─── Filter State ─────────────────────────────────────────────────────────────

export interface FilterState {
  scenario: BusinessScenario;
  dateRange: string;
  segment: string;
  startDate: string;
  endDate: string;
}

// ─── Generic ──────────────────────────────────────────────────────────────────

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  field: string;
  direction: SortDirection;
}

export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: unknown, row: T) => React.ReactNode;
}
