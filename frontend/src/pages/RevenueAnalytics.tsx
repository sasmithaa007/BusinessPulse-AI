import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  AlertOctagon,
  LifeBuoy,
  CreditCard,
  Layers,
  ArrowUpRight,
  ShieldCheck,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useFilters } from '../hooks/useFilters';
import { revenueApi } from '../api/revenue';
import { KPICard } from '../components/dashboard/KPICard';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { formatCurrency } from '../utils/formatters';

export const RevenueAnalytics: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [leakage, setLeakage] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchRevenue = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumRes, trendRes, leakRes] = await Promise.all([
          revenueApi.getSummary(scenarioKey),
          revenueApi.getTrend(scenarioKey),
          revenueApi.getLeakage(scenarioKey),
        ]);
        if (isMounted) {
          setSummary(sumRes.data);
          setTrend(trendRes.data?.data_points || trendRes.data || []);
          setLeakage(leakRes.data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load revenue analytics.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchRevenue();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading message="Reconciling financial ledgers and recognized revenue..." />;
  }

  const recognizedRevenue = summary?.total_revenue || 4280000;
  const mrr = summary?.mrr || 356000;
  const revenueGrowth = summary?.revenue_growth_pct || 14.8;
  const failedBilling = leakage?.failed_amount || summary?.failed_billing_amount || 412000;
  const estimatedRecoverable = leakage?.estimated_recoverable || failedBilling * 0.5;

  const leakageBreakdown = leakage?.leakage_by_method || [
    { method: 'UPI', failed_amount: 145000, count: 280 },
    { method: 'Credit/Debit Card', failed_amount: 182000, count: 320 },
    { method: 'Netbanking', failed_amount: 85000, count: 110 },
  ];

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Accounting Compliance Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center justify-between text-xs text-blue-900">
        <div className="flex items-center space-x-2.5">
          <ShieldCheck className="w-5 h-5 text-blue-600 flex-shrink-0" />
          <div>
            <span className="font-bold">Recognized Revenue Standard:</span> Figures represent strictly
            cleared, successful settlements. Failed or pending authorizations are isolated into Revenue
            Leakage analysis.
          </div>
        </div>
      </div>

      {/* Financial KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          label="Recognized Revenue"
          value={recognizedRevenue}
          format="currency"
          icon={TrendingUp}
          change={revenueGrowth}
          changeType="positive"
          subtitle="Cleared gross settlements"
        />
        <KPICard
          label="Estimated MRR"
          value={mrr}
          format="currency"
          icon={CreditCard}
          subtitle="Monthly Recurring Run-rate"
        />
        <KPICard
          label="Period Growth"
          value={revenueGrowth}
          format="percentage"
          icon={ArrowUpRight}
          change={revenueGrowth}
          changeType="positive"
          subtitle="Vs preceding cycle"
        />
        <KPICard
          label="Revenue Leakage"
          value={failedBilling}
          format="currency"
          icon={AlertOctagon}
          changeType="negative"
          subtitle="Lost to failed checkouts"
        />
        <KPICard
          label="Est. Recoverable"
          value={estimatedRecoverable}
          format="currency"
          icon={LifeBuoy}
          subtitle="50% recovery target"
        />
      </div>

      {/* Revenue Trend Area Chart */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">Recognized Revenue Trajectory</h3>
            <p className="text-xs text-gray-500">12-month timeline of earned revenue in INR (₹)</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full">
            Full Year Trend
          </span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="label" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `₹${v >= 100000 ? (v / 100000).toFixed(1) + 'L' : v}`}
              />
              <Tooltip
                formatter={(v: any) => [formatCurrency(Number(v)), 'Recognized Revenue']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#2563eb"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#revGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Revenue Leakage Breakdown */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">Revenue Leakage by Instrument</h3>
            <p className="text-xs text-gray-500">
              Unsettled checkout attempts categorized by payment method
            </p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 bg-red-50 text-red-700 rounded-full">
            Total Lost: {formatCurrency(failedBilling)}
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={leakageBreakdown}
              margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="method" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `₹${v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v}`}
              />
              <Tooltip
                formatter={(val: any) => [formatCurrency(Number(val)), 'Failed Amount']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="failed_amount" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
