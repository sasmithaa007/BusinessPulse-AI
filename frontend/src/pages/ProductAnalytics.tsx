import React, { useEffect, useState } from 'react';
import { Package, Users, Activity, Zap } from 'lucide-react';
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

export const ProductAnalytics: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [features, setFeatures] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchProductData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [usageRes, featRes] = await Promise.all([
          api.get(`/products/usage?scenario=${scenarioKey}`),
          api.get(`/products/features?scenario=${scenarioKey}`),
        ]);
        if (isMounted) {
          setSummary(usageRes.data);
          setFeatures(featRes.data?.features || featRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load product analytics.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchProductData();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading message="Analyzing product telemetry and feature adoption rates..." />;
  }

  const activeUsers = summary?.active_users || 1280;
  const totalEvents = summary?.total_usage_events || 28400;
  const topFeature = summary?.top_feature || 'Portfolio Analyzer';
  const avgAdoption = summary?.avg_adoption_rate || 42.6;

  const defaultFeatures = [
    { feature_name: 'Mutual Funds / SIP', adoption_rate: 64.2, unique_users: 1150, usage_count: 8200 },
    { feature_name: 'Equities Order Book', adoption_rate: 58.5, unique_users: 1050, usage_count: 7400 },
    { feature_name: 'Tax Harvesting Tool', adoption_rate: 34.0, unique_users: 610, usage_count: 2900 },
    { feature_name: 'Direct Gold Assets', adoption_rate: 22.8, unique_users: 410, usage_count: 1800 },
  ];

  const featureList = features.length > 0 ? features : defaultFeatures;

  const columns: Column<any>[] = [
    {
      key: 'feature_name',
      header: 'Feature Module',
      render: (row) => (
        <span className="font-semibold text-gray-900">{row.feature_name}</span>
      ),
    },
    {
      key: 'adoption_rate',
      header: 'Adoption Rate',
      sortable: true,
      render: (row) => (
        <div className="flex items-center space-x-2">
          <div className="w-20 bg-gray-100 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-blue-600 h-1.5 rounded-full"
              style={{ width: `${Math.min(row.adoption_rate || 0, 100)}%` }}
            />
          </div>
          <span className="text-xs font-bold text-gray-700">{row.adoption_rate}%</span>
        </div>
      ),
    },
    {
      key: 'unique_users',
      header: 'Unique Users',
      sortable: true,
      render: (row) => (
        <span className="text-xs text-gray-700 font-mono">
          {Number(row.unique_users || 0).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'usage_count',
      header: 'Cumulative Invocations',
      sortable: true,
      render: (row) => (
        <span className="text-xs text-gray-700 font-mono">
          {Number(row.usage_count || 0).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Active Product Users"
          value={activeUsers}
          format="number"
          icon={Users}
          subtitle="Unique active accounts"
        />
        <KPICard
          label="Total Usage Invocations"
          value={totalEvents}
          format="number"
          icon={Activity}
          subtitle="Events recorded"
        />
        <KPICard
          label="Leading Feature"
          value={topFeature}
          format="raw"
          icon={Zap}
          subtitle="Highest engagement"
        />
        <KPICard
          label="Mean Feature Adoption"
          value={avgAdoption}
          format="percentage"
          icon={Package}
          subtitle="Across product catalog"
        />
      </div>

      {/* Feature Adoption Horizontal Bar Chart */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">Feature Adoption Ranking</h3>
            <p className="text-xs text-gray-500">
              Percentage of total accounts utilizing specific features
            </p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full">
            Active Workspace
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={featureList}
              layout="vertical"
              margin={{ top: 10, right: 20, left: 120, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis
                type="number"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                tickFormatter={(v) => `${v}%`}
              />
              <YAxis
                type="category"
                dataKey="feature_name"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                formatter={(val: any) => [`${val}%`, 'Adoption Rate']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="adoption_rate" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feature Engagement Table */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-gray-800">Feature Engagement Ledger</h3>
        <DataTable columns={columns} data={featureList} total={featureList.length} />
      </div>
    </div>
  );
};
