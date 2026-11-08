import { format, parseISO, isValid } from 'date-fns';

/**
 * Formats a number as Indian Rupee currency using the Indian number system.
 * e.g. 123456 → ₹1,23,456
 */
export function formatCurrency(amount: number): string {
  if (!isFinite(amount)) return '₹0';

  // Use Intl.NumberFormat with Indian locale for the Indian numbering system
  const formatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);

  return formatted;
}

/**
 * Formats a number with Indian comma grouping (1,23,456).
 */
export function formatNumber(num: number): string {
  if (!isFinite(num)) return '0';
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Formats a decimal as a percentage string.
 * e.g. 0.125 or 12.5 → '12.5%'
 * Values > 1 are treated as already-percentage values.
 */
export function formatPercentage(value: number, decimals = 1): string {
  if (!isFinite(value)) return '0%';
  // Treat values ≤ 1 as fractions, otherwise already a percentage
  const pct = Math.abs(value) <= 1 ? value * 100 : value;
  return `${pct.toFixed(decimals)}%`;
}

/**
 * Formats an ISO date string as 'Nov 08, 2024'.
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return '—';
  try {
    const date = parseISO(dateStr);
    if (!isValid(date)) return dateStr;
    return format(date, 'MMM dd, yyyy');
  } catch {
    return dateStr;
  }
}

/**
 * Formats an ISO date-time string as 'Nov 08, 2024 14:30'.
 */
export function formatDateTime(dateStr: string): string {
  if (!dateStr) return '—';
  try {
    const date = parseISO(dateStr);
    if (!isValid(date)) return dateStr;
    return format(date, 'MMM dd, yyyy HH:mm');
  } catch {
    return dateStr;
  }
}

/**
 * Formats a duration in milliseconds to a human-readable string.
 * e.g. 1200 → '1.2s', 450 → '450ms'
 */
export function formatDuration(ms: number): string {
  if (!isFinite(ms) || ms < 0) return '0ms';
  if (ms >= 1000) {
    return `${(ms / 1000).toFixed(1)}s`;
  }
  return `${Math.round(ms)}ms`;
}

/**
 * Returns a Tailwind text-color class based on the change type.
 */
export function getChangeColor(changeType: string): string {
  switch (changeType) {
    case 'positive':
      return 'text-green-600';
    case 'negative':
      return 'text-red-600';
    case 'neutral':
    default:
      return 'text-gray-500';
  }
}

/**
 * Returns a Tailwind background-color class based on the change type.
 */
export function getChangeBgColor(changeType: string): string {
  switch (changeType) {
    case 'positive':
      return 'bg-green-50 text-green-700';
    case 'negative':
      return 'bg-red-50 text-red-700';
    case 'neutral':
    default:
      return 'bg-gray-50 text-gray-600';
  }
}

/**
 * Truncates text to a maximum length, appending '…' if truncated.
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength).trimEnd()}…`;
}

/**
 * Maps a business scenario key to its display label.
 * e.g. 'fintech' → 'FinTech', 'saas' → 'SaaS', 'developer_tools' → 'Developer Tools'
 */
export function scenarioLabel(scenario: string): string {
  const map: Record<string, string> = {
    fintech: 'FinTech',
    saas: 'SaaS',
    developer_tools: 'Developer Tools',
  };
  return map[scenario] ?? scenario;
}

/**
 * Formats large numbers in a compact, readable way.
 * e.g. 1500000 → '₹15L', 10000000 → '₹1Cr'
 */
export function formatCompactCurrency(amount: number): string {
  if (!isFinite(amount)) return '₹0';
  if (amount >= 10_000_000) {
    return `₹${(amount / 10_000_000).toFixed(1)}Cr`;
  }
  if (amount >= 100_000) {
    return `₹${(amount / 100_000).toFixed(1)}L`;
  }
  if (amount >= 1_000) {
    return `₹${(amount / 1_000).toFixed(1)}K`;
  }
  return `₹${amount.toFixed(0)}`;
}

/**
 * Formats a compact number without currency symbol.
 * e.g. 1500 → '1.5K', 1500000 → '1.5M'
 */
export function formatCompactNumber(num: number): string {
  if (!isFinite(num)) return '0';
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return String(Math.round(num));
}

/**
 * Returns a priority badge color class.
 */
export function getPriorityColor(priority: 'high' | 'medium' | 'low'): string {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-700';
    case 'medium':
      return 'bg-amber-100 text-amber-700';
    case 'low':
      return 'bg-green-100 text-green-700';
  }
}

/**
 * Returns an evidence level badge color class.
 */
export function getEvidenceColor(evidence: 'confirmed' | 'correlation' | 'hypothesis'): string {
  switch (evidence) {
    case 'confirmed':
      return 'bg-blue-100 text-blue-700';
    case 'correlation':
      return 'bg-purple-100 text-purple-700';
    case 'hypothesis':
      return 'bg-gray-100 text-gray-600';
  }
}

/**
 * Returns a customer status badge color class.
 */
export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
    case 'completed':
      return 'bg-green-100 text-green-700';
    case 'inactive':
    case 'pending':
    case 'paused':
      return 'bg-amber-100 text-amber-700';
    case 'churned':
    case 'failed':
    case 'cancelled':
      return 'bg-red-100 text-red-700';
    case 'refunded':
      return 'bg-blue-100 text-blue-700';
    default:
      return 'bg-gray-100 text-gray-600';
  }
}

/**
 * Formats a churn risk score (0-1) with a color class.
 */
export function getChurnRiskColor(score: number): string {
  if (score >= 0.7) return 'text-red-600';
  if (score >= 0.4) return 'text-amber-600';
  return 'text-green-600';
}

/**
 * Returns a formatted churn risk label.
 */
export function getChurnRiskLabel(score: number): string {
  if (score >= 0.7) return 'High Risk';
  if (score >= 0.4) return 'Medium Risk';
  return 'Low Risk';
}
