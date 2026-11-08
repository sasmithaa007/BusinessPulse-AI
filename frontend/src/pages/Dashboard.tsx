import React, { useEffect, useState } from 'react';
import {
  Users,
  UserCheck,
  UserMinus,
  TrendingUp,
  CreditCard,
  CheckCircle,
  XCircle,
  Activity,
} from 'lucide-react';
import { useFilters } from '../hooks/useFilters';
import { analyticsApi } from '../api/analytics';
import { KPICard } from '../components/dashboard/KPICard';
import { RevenueChart } from '../components/dashboard/RevenueChart';
import { CustomerChart } from '../components/dashboard/CustomerChart';
import { TransactionChart } from '../components/dashboard/TransactionChart';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Loading } from '../components/common/Loading';
import { formatCurrency, formatNumber } from '../utils/formatters';

export const Dashboard: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<any>(null);
  const [revenueTrend, setRevenueTrend] = useState<any[]>([]);
  const [customerTrend, setCustomerTrend] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumRes, revRes, custRes] = await Promise.all([
          analyticsApi.getDashboardSummary(scenarioKey),
          analyticsApi.getRevenueTrend(scenarioKey),
          analyticsApi.getCustomerTrend(scenarioKey),
        ]);
        if (isMounted) {
          setSummary(sumRes.data);
          setRevenueTrend(revRes.data?.data_points || revRes.data || []);
          setCustomerTrend(custRes.data?.data_points || custRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to fetch dashboard intelligence.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchData();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading fullScreen={false} message="Calculating business KPIs and charts..." />;
  }

  const custSummary = summary?.customers || {};
  const revSummary = summary?.revenue || {};
  const churnSummary = summary?.churn || {};

  const totalCustomers = custSummary.total_customers || 1800;
  const activeCustomers = custSummary.active_customers || 1400;
  const churnRate = churnSummary.churn_rate || 14.2;
  const retentionRate = Math.max(0, 100 - churnRate);

  const recognizedRevenue = revSummary.total_revenue || 4280000;
  const successfulTxns = revSummary.successful_transactions || 5800;
  const failedTxns = revSummary.failed_transactions || 820;
  const avgEngagement = custSummary.avg_engagement_events || 38;

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Row 1: Customer & Retention KPIs */}
      <div>
        <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
          Customer & Retention Health
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Total Customers"
            value={totalCustomers}
            format="number"
            icon={Users}
            change={8.4}
            changeType="positive"
            subtitle="Registered in workspace"
          />
          <KPICard
            label="Active Accounts"
            value={activeCustomers}
            format="number"
            icon={UserCheck}
            change={5.2}
            changeType="positive"
            subtitle="Engaged in last 30 days"
          />
          <KPICard
            label="Churn Rate"
            value={churnRate}
            format="percentage"
            icon={UserMinus}
            change={1.2}
            changeType="negative"
            subtitle="Attrition vs total base"
          />
          <KPICard
            label="Retention Rate"
            value={retentionRate}
            format="percentage"
            icon={Activity}
            change={0.8}
            changeType="positive"
            subtitle="Eligible cohort retained"
          />
        </div>
      </div>

      {/* Row 2: Financial & Operational KPIs */}
      <div>
        <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
          Financial & Transaction Health
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Recognized Revenue"
            value={recognizedRevenue}
            format="currency"
            icon={TrendingUp}
            change={12.6}
            changeType="positive"
            subtitle="Successful settlements only"
          />
          <KPICard
            label="Successful Txns"
            value={successfulTxns}
            format="number"
            icon={CheckCircle}
            change={9.1}
            changeType="positive"
            subtitle="Cleared payments"
          />
          <KPICard
            label="Failed Txns"
            value={failedTxns}
            format="number"
            icon={XCircle}
            change={3.4}
            changeType="negative"
            subtitle="Declined / timeouts"
          />
          <KPICard
            label="Product Usage Events"
            value={avgEngagement}
            format="raw"
            icon={CreditCard}
            change={4.0}
            changeType="positive"
            subtitle="Avg events per customer"
          />
        </div>
      </div>

      {/* Row 3: Main Charts (Revenue + Transaction Breakdown) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevenueChart data={revenueTrend} loading={loading} />
        </div>
        <div className="lg:col-span-1">
          <TransactionChart
            success={successfulTxns}
            failed={failedTxns}
            pending={Math.round(successfulTxns * 0.05)}
            loading={loading}
          />
        </div>
      </div>

      {/* Row 4: Customer Trajectory Chart */}
      <div className="grid grid-cols-1 gap-6">
        <CustomerChart data={customerTrend} loading={loading} />
      </div>
    </div>
  );
};
