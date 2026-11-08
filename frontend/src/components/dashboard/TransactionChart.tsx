import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface TransactionBreakdownProps {
  success: number;
  failed: number;
  pending?: number;
  loading?: boolean;
}

const COLORS = ['#10b981', '#ef4444', '#f59e0b'];

export const TransactionChart: React.FC<TransactionBreakdownProps> = ({
  success,
  failed,
  pending = 0,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 h-80 flex items-center justify-center animate-pulse">
        <div className="text-gray-400 text-sm">Loading transaction breakdown...</div>
      </div>
    );
  }

  const data = [
    { name: 'Successful', value: success },
    { name: 'Failed', value: failed },
    { name: 'Pending', value: pending },
  ].filter((d) => d.value > 0);

  const total = success + failed + pending;
  const successRate = total > 0 ? ((success / total) * 100).toFixed(1) : '0';

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-base font-semibold text-gray-900">Transaction Health</h3>
          <p className="text-xs text-gray-500">Attempted settlement outcomes</p>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 bg-green-50 text-green-700 rounded-full">
          {successRate}% Success
        </span>
      </div>

      <div className="h-60 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(val: any) => [Number(val).toLocaleString(), 'Count']}
              contentStyle={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
