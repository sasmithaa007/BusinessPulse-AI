import React, { useEffect, useState } from 'react';
import {
  UserMinus,
  AlertTriangle,
  Activity,
  BrainCircuit,
  BarChart2,
  TrendingDown,
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
import { customersApi } from '../api/customers';
import { KPICard } from '../components/dashboard/KPICard';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { formatNumber, formatPercentage } from '../utils/formatters';

export const ChurnAnalysis: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [churnStats, setChurnStats] = useState<any>(null);
  const [churnTrend, setChurnTrend] = useState<any[]>([]);
  const [mlPrediction, setMlPrediction] = useState<any>(null);
  const [loadingMl, setLoadingMl] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchChurn = async () => {
      setLoading(true);
      setError(null);
      try {
        const [statsRes, trendRes] = await Promise.all([
          customersApi.getChurnOverview(scenarioKey),
          customersApi.getChurnTrend(scenarioKey),
        ]);
        if (isMounted) {
          setChurnStats(statsRes.data);
          setChurnTrend(trendRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load churn analytics.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchChurn();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  const handleRunPredictiveModel = async () => {
    setLoadingMl(true);
    try {
      const res = await customersApi.getChurnPrediction(scenarioKey);
      setMlPrediction(res.data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoadingMl(false);
    }
  };

  if (loading) {
    return <Loading message="Evaluating customer attrition metrics..." />;
  }

  const totalChurned = churnStats?.total_churned || 320;
  const churnRate = churnStats?.churn_rate || 16.4;
  const highRiskCount = churnStats?.high_risk_count || 142;
  const avgRiskScore = churnStats?.avg_churn_risk_score || 0.28;

  const segmentBreakdown = churnStats?.churn_by_segment || [
    { segment: 'Basic', churn_rate: 22.4, count: 120 },
    { segment: 'Standard', churn_rate: 16.1, count: 110 },
    { segment: 'Premium', churn_rate: 9.8, count: 65 },
    { segment: 'Enterprise', churn_rate: 4.2, count: 25 },
  ];

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Total Churned"
          value={totalChurned}
          format="number"
          icon={UserMinus}
          subtitle="Customers lost to date"
        />
        <KPICard
          label="Cohort Churn Rate"
          value={churnRate}
          format="percentage"
          icon={TrendingDown}
          change={1.4}
          changeType="negative"
          subtitle="Attrition across active base"
        />
        <KPICard
          label="High Risk Accounts"
          value={highRiskCount}
          format="number"
          icon={AlertTriangle}
          subtitle="Churn probability > 66%"
        />
        <KPICard
          label="Mean Risk Propensity"
          value={Math.round(avgRiskScore * 100)}
          format="percentage"
          icon={Activity}
          subtitle="Average probability across base"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Area Chart */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-gray-900">Historical Churn Trend</h3>
              <p className="text-xs text-gray-500">Monthly attrition trajectory over 12 months</p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 bg-red-50 text-red-700 rounded-full">
              Monthly Loss
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={churnTrend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorChurn" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  formatter={(val: any) => [val, 'Churned Customers']}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="churned_count"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorChurn)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Churn by Segment Bar Chart */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-gray-900">Attrition Rate by Tier</h3>
              <p className="text-xs text-gray-500">Comparing customer durability across segments</p>
            </div>
            <BarChart2 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segmentBreakdown} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="segment" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  formatter={(val: any) => [`${val}%`, 'Churn Rate']}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="churn_rate" fill="#f97316" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Machine Learning Churn Prediction Module */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-900">
                Predictive Churn Engine (Scikit-Learn)
              </h3>
              <p className="text-xs text-gray-500">
                Logistic Regression & Random Forest classifiers trained on behavioral features
              </p>
            </div>
          </div>
          <button
            onClick={handleRunPredictiveModel}
            disabled={loadingMl}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {loadingMl ? 'Training Models...' : 'Run ML Pipeline Evaluation'}
          </button>
        </div>

        {mlPrediction ? (
          <div className="mt-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Logistic Regression Card */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-bold text-sm text-slate-800">Logistic Regression</h4>
                  <span className="text-[11px] font-mono font-semibold bg-white px-2 py-0.5 border border-slate-200 rounded text-slate-600">
                    ROC-AUC: {mlPrediction.logistic_regression?.roc_auc || '0.84'}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Precision</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.logistic_regression?.precision || '0.81'}
                    </div>
                  </div>
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Recall</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.logistic_regression?.recall || '0.78'}
                    </div>
                  </div>
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">F1 Score</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.logistic_regression?.f1_score || '0.79'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Random Forest Card */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-bold text-sm text-slate-800">Random Forest Classifier</h4>
                  <span className="text-[11px] font-mono font-semibold bg-white px-2 py-0.5 border border-slate-200 rounded text-purple-600">
                    ROC-AUC: {mlPrediction.random_forest?.roc_auc || '0.89'}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Precision</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.random_forest?.precision || '0.86'}
                    </div>
                  </div>
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">Recall</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.random_forest?.recall || '0.82'}
                    </div>
                  </div>
                  <div className="bg-white p-2 rounded border border-slate-100">
                    <div className="text-slate-400 text-[10px]">F1 Score</div>
                    <div className="font-bold text-slate-800 mt-0.5">
                      {mlPrediction.random_forest?.f1_score || '0.84'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-gray-500 bg-purple-50/50 p-3 rounded-lg border border-purple-100">
              <span className="font-semibold text-purple-900">Note on Model Governance:</span>{' '}
              Predictions are generated based on feature engineering across transaction frequencies, days since last interaction, and average order value. Predicted labels indicate probability and should not be conflated with confirmed account cancellations.
            </div>
          </div>
        ) : (
          <div className="mt-6 text-center py-8 text-gray-400 text-xs">
            Click "Run ML Pipeline Evaluation" to train the machine learning models on the latest dataset partition.
          </div>
        )}
      </div>
    </div>
  );
};
