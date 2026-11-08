import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/formatters';

interface KPICardProps {
  label: string;
  value: number | string;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  format?: 'number' | 'currency' | 'percentage' | 'raw';
  subtitle?: string;
  loading?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  format = 'raw',
  subtitle,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 animate-pulse">
        <div className="flex items-center justify-between mb-3">
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="w-9 h-9 bg-gray-200 rounded-lg"></div>
        </div>
        <div className="h-8 bg-gray-200 rounded w-32 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-20"></div>
      </div>
    );
  }

  const formatDisplayValue = () => {
    if (typeof value === 'string') return value;
    switch (format) {
      case 'currency':
        return formatCurrency(value);
      case 'number':
        return formatNumber(value);
      case 'percentage':
        return formatPercentage(value);
      default:
        return value;
    }
  };

  const getTrendBadge = () => {
    if (change === undefined) return null;
    const isPositive = changeType === 'positive' || (changeType === 'neutral' && change >= 0);
    const isNegative = changeType === 'negative';

    return (
      <span
        className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
          isNegative
            ? 'bg-red-50 text-red-600'
            : isPositive
            ? 'bg-green-50 text-green-600'
            : 'bg-gray-100 text-gray-600'
        }`}
      >
        {isNegative ? (
          <TrendingDown className="w-3 h-3 mr-1" />
        ) : isPositive ? (
          <TrendingUp className="w-3 h-3 mr-1" />
        ) : (
          <Minus className="w-3 h-3 mr-1" />
        )}
        {Math.abs(change)}%
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {label}
        </span>
        <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <div className="text-2xl font-bold text-gray-900 tracking-tight">
          {formatDisplayValue()}
        </div>
        {getTrendBadge()}
      </div>

      {subtitle && (
        <p className="mt-1 text-xs text-gray-500 font-medium">{subtitle}</p>
      )}
    </div>
  );
};
