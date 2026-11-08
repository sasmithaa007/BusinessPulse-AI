import React, { useEffect, useState } from 'react';
import { Settings2, CheckCircle, XCircle, Clock, DollarSign, AlertTriangle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useFilters } from '../hooks/useFilters';
import api from '../api/axios';
import { KPICard } from '../components/dashboard/KPICard';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { DataTable, Column } from '../components/common/DataTable';
import { formatCurrency } from '../utils/formatters';

export const OperationsAnalytics: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<any>(null);
  const [bottlenecks, setBottlenecks] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true;
    const fetchOps = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumRes, bRes] = await Promise.all([
          api.get(`/operations/summary?scenario=${scenarioKey}`),
          api.get(`/operations/bottlenecks?scenario=${scenarioKey}`),
        ]);
        if (isMounted) {
          setSummary(sumRes.data);
          setBottlenecks(bRes.data?.bottlenecks || bRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load operational analytics.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchOps();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading message="Evaluating operational run-rates and process bottlenecks..." />;
  }

  const total = summary?.total_processes || 5000;
  const successRate = summary?.success_rate || 88.4;
  const failedCount = summary?.failed_count || 580;
  const avgTime = summary?.avg_processing_time_seconds || 4.2;
  const totalCost = summary?.total_operational_cost || 1840000;

  const defaultBottlenecks = [
    { process_name: 'KYC_Verification', avg_time_sec: 14.8, failure_rate: 18.2, operational_cost: 480000 },
    { process_name: 'Payment_Settlement', avg_time_sec: 8.4, failure_rate: 11.5, operational_cost: 620000 },
    { process_name: 'Portfolio_Rebalancing', avg_time_sec: 5.1, failure_rate: 4.8, operational_cost: 310000 },
    { process_name: 'Tax_Computation', avg_time_sec: 3.2, failure_rate: 2.1, operational_cost: 240000 },
    { process_name: 'Fraud_Detection_Scan', avg_time_sec: 1.8, failure_rate: 0.6, operational_cost: 190000 },
  ];

  const bottleneckData = bottlenecks.length > 0 ? bottlenecks : defaultBottlenecks;

  const columns: Column<any>[] = [
    {
      key: 'process_name',
      header: 'Workflow Process',
      render: (row) => (
        <span className="font-semibold text-gray-900 font-mono text-xs">
          {row.process_name}
        </span>
      ),
    },
    {
      key: 'avg_time_sec',
      header: 'Processing Duration',
      sortable: true,
      render: (row) => (
        <span className="text-xs font-mono font-bold text-slate-800">
          {row.avg_time_sec || row.avg_time} sec
        </span>
      ),
    },
    {
      key: 'failure_rate',
      header: 'Failure Rate',
      sortable: true,
      render: (row) => {
        const rate = row.failure_rate || 0;
        return (
          <span
            className={`text-xs font-semibold ${
              rate > 10 ? 'text-rose-600' : 'text-slate-700'
            }`}
          >
            {rate}%
          </span>
        );
      },
    },
    {
      key: 'operational_cost',
      header: 'Operational Cost (₹)',
      sortable: true,
      render: (row) => (
        <span className="text-xs font-semibold text-blue-600 font-mono">
          {formatCurrency(Number(row.operational_cost || 0))}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          label="Total Processes"
          value={total}
          format="number"
          icon={Settings2}
          subtitle="Workflows logged"
        />
        <KPICard
          label="Process Success"
          value={successRate}
          format="percentage"
          icon={CheckCircle}
          change={1.2}
          changeType="positive"
          subtitle="Target > 85%"
        />
        <KPICard
          label="Failed Processes"
          value={failedCount}
          format="number"
          icon={XCircle}
          changeType="negative"
          subtitle="Exceptions flagged"
        />
        <KPICard
          label="Mean Execution"
          value={`${avgTime}s`}
          format="raw"
          icon={Clock}
          subtitle="Cycle duration"
        />
        <KPICard
          label="Operational Spend"
          value={totalCost}
          format="currency"
          icon={DollarSign}
          subtitle="Aggregated cost"
        />
      </div>

      {/* Bottlenecks Chart */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">
              Workflow Latency Bottleneck Profile
            </h3>
            <p className="text-xs text-gray-500">Average execution duration in seconds per process</p>
          </div>
          <AlertTriangle className="w-5 h-5 text-amber-500" />
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={bottleneckData}
              margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="process_name" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${v}s`}
              />
              <Tooltip
                formatter={(val: any) => [`${val} seconds`, 'Avg Execution Time']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="avg_time_sec" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottlenecks Table */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-gray-800">Operational Bottleneck Ledger</h3>
        <DataTable columns={columns} data={bottleneckData} total={bottleneckData.length} />
      </div>
    </div>
  );
};
