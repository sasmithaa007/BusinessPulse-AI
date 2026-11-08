import React from 'react';
import { Calendar } from 'lucide-react';
import { DateRange, useFilters } from '../../hooks/useFilters';

export const DateFilter: React.FC = () => {
  const { dateRange, setDateRange } = useFilters();

  return (
    <div className="inline-flex items-center space-x-2 bg-white border border-gray-200 rounded-lg px-3 py-1.5 shadow-sm">
      <Calendar className="w-4 h-4 text-gray-500" />
      <select
        value={dateRange}
        onChange={(e) => setDateRange(e.target.value as DateRange)}
        className="text-xs font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
      >
        <option value="last7">Last 7 Days</option>
        <option value="last30">Last 30 Days</option>
        <option value="last90">Last 90 Days</option>
        <option value="last6months">Last 6 Months</option>
        <option value="lastYear">Last 1 Year</option>
        <option value="allTime">All Time</option>
      </select>
    </div>
  );
};
