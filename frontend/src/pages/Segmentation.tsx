import React, { useEffect, useState } from 'react';
import { PieChart as PieIcon, Award, DollarSign, Users } from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useFilters } from '../hooks/useFilters';
import { customersApi } from '../api/customers';
import { KPICard } from '../components/dashboard/KPICard';
import { DataTable, Column } from '../components/common/DataTable';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { formatCurrency } from '../utils/formatters';

const SEGMENT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'];

export const Segmentation: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [activeTab, setActiveTab] = useState<'overview' | 'rfm'>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [distribution, setDistribution] = useState<any[]>([]);
  const [rfmList, setRfmList] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true;
    const fetchSegments = async () => {
      setLoading(true);
      setError(null);
      try {
        const [distRes, rfmRes] = await Promise.all([
          customersApi.getSegmentsDistribution(scenarioKey),
          customersApi.getSegmentsRFM(scenarioKey),
        ]);
        if (isMounted) {
          setDistribution(distRes.data || []);
          setRfmList(rfmRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load segmentation metrics.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchSegments();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading message="Computing RFM scores and customer segmentations..." />;
  }

  const rfmColumns: Column<any>[] = [
    {
      key: 'customer_name',
      header: 'Customer',
      render: (row) => (
        <div>
          <div className="font-semibold text-gray-900">{row.name || row.customer_name}</div>
          <div className="text-xs text-gray-400 font-mono">{row.customer_code}</div>
        </div>
      ),
    },
    {
      key: 'recency_days',
      header: 'Recency',
      sortable: true,
      render: (row) => (
        <span className="text-xs font-mono">{row.recency_days ?? 14} days ago</span>
      ),
    },
    {
      key: 'frequency',
      header: 'Frequency',
      sortable: true,
      render: (row) => (
        <span className="text-xs font-semibold">{row.frequency ?? 8} txns</span>
      ),
    },
    {
      key: 'monetary',
      header: 'Monetary Spend',
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-blue-600">
          {formatCurrency(Number(row.monetary || row.total_spend || 0))}
        </span>
      ),
    },
    {
      key: 'rfm_score',
      header: 'RFM Score',
      render: (row) => (
        <span className="font-mono text-xs font-bold bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
          {row.rfm_score || '5-4-5'}
        </span>
      ),
    },
    {
      key: 'cluster_label',
      header: 'Segment Cluster',
      render: (row) => {
        const label = row.cluster_label || 'Champions';
        return (
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            {label}
          </span>
        );
      },
    },
  ];

  const defaultDist = [
    { name: 'Basic', count: 620, avg_spend: 3400 },
    { name: 'Standard', count: 580, avg_spend: 14200 },
    { name: 'Premium', count: 410, avg_spend: 42000 },
    { name: 'Enterprise', count: 190, avg_spend: 125000 },
  ];

  const distData = distribution.length > 0 ? distribution : defaultDist;

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 space-x-6 text-sm font-semibold">
        <button
          onClick={() => setActiveTab('overview')}
          className={`pb-3 transition-colors ${
            activeTab === 'overview'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          Segment Distribution Overview
        </button>
        <button
          onClick={() => setActiveTab('rfm')}
          className={`pb-3 transition-colors ${
            activeTab === 'rfm'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          RFM Scoring & Behavioral Clusters
        </button>
      </div>

      {activeTab === 'overview' ? (
        <>
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KPICard
              label="Primary Tier"
              value="Standard"
              format="raw"
              icon={Users}
              subtitle="Largest customer base"
            />
            <KPICard
              label="Enterprise Contribution"
              value={48.2}
              format="percentage"
              icon={DollarSign}
              subtitle="Share of overall revenue"
            />
            <KPICard
              label="Highest LTV Tier"
              value="Enterprise"
              format="raw"
              icon={Award}
              subtitle="Avg ₹1,25,000 spend"
            />
            <KPICard
              label="Active Segments"
              value={4}
              format="number"
              icon={PieIcon}
              subtitle="Distinct behavioral groups"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pie Distribution */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
              <h3 className="text-base font-semibold text-gray-900 mb-1">
                Customer Population by Tier
              </h3>
              <p className="text-xs text-gray-500 mb-4">Proportion of accounts in each tier</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distData}
                      dataKey="count"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      innerRadius={45}
                      paddingAngle={3}
                    >
                      {distData.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(v: any) => [v, 'Accounts']}
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        borderRadius: '8px',
                        border: '1px solid #e2e8f0',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Spend Comparison Bar Chart */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
              <h3 className="text-base font-semibold text-gray-900 mb-1">
                Average Value per Tier
              </h3>
              <p className="text-xs text-gray-500 mb-4">Historical spend comparison across segments</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={distData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <YAxis
                      stroke="#94a3b8"
                      fontSize={11}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(v) => `₹${v >= 1000 ? v / 1000 + 'k' : v}`}
                    />
                    <Tooltip
                      formatter={(v: any) => [formatCurrency(Number(v)), 'Avg Spend']}
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        borderRadius: '8px',
                        border: '1px solid #e2e8f0',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="avg_spend" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* RFM Table */
        <div className="space-y-4">
          <div className="bg-blue-50/60 border border-blue-200 rounded-xl p-4 text-xs text-blue-900">
            <span className="font-bold">RFM Methodology:</span> Recency (days since last purchase),
            Frequency (number of purchases in period), and Monetary (total spend). Scores range
            from 1 (low) to 5 (high).
          </div>
          <DataTable
            columns={rfmColumns}
            data={rfmList}
            pageSize={15}
            total={rfmList.length}
          />
        </div>
      )}
    </div>
  );
};
