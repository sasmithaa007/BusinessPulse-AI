import React, { useEffect, useState } from 'react';
import {
  CreditCard,
  CheckCircle2,
  XCircle,
  Clock,
  Filter,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
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
import { transactionsApi } from '../api/transactions';
import { KPICard } from '../components/dashboard/KPICard';
import { DataTable, Column } from '../components/common/DataTable';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { formatCurrency, formatDateTime } from '../utils/formatters';

export const TransactionAnalytics: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<any>(null);
  const [failures, setFailures] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [totalTxns, setTotalTxns] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);

  const [statusFilter, setStatusFilter] = useState('');
  const [methodFilter, setMethodFilter] = useState('');

  const fetchTransactions = async () => {
    try {
      const res = await transactionsApi.getTransactions({
        scenario: scenarioKey,
        skip: (page - 1) * pageSize,
        limit: pageSize,
        status: statusFilter || undefined,
        payment_method: methodFilter || undefined,
      });
      setTransactions(res.data?.items || []);
      setTotalTxns(res.data?.total || 0);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    let isMounted = true;
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumRes, failRes] = await Promise.all([
          transactionsApi.getSummary(scenarioKey),
          transactionsApi.getFailures(scenarioKey),
        ]);
        if (isMounted) {
          setSummary(sumRes.data);
          setFailures(failRes.data?.reasons || failRes.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load transaction data.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchAnalytics();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  useEffect(() => {
    fetchTransactions();
  }, [scenarioKey, page, statusFilter, methodFilter]);

  if (loading) {
    return <Loading message="Auditing gateway records and settlement outcomes..." />;
  }

  const total = summary?.total_transactions || 6200;
  const successful = summary?.successful_transactions || 5270;
  const failed = summary?.failed_transactions || 930;
  const successRate = summary?.success_rate || 85.0;
  const failureRate = summary?.failure_rate || 15.0;
  const avgValue = summary?.avg_transaction_value || 1420;

  const defaultFailures = [
    { reason: 'Insufficient funds', count: 340 },
    { reason: 'Bank network timeout', count: 260 },
    { reason: 'Card declined by issuer', count: 180 },
    { reason: 'Daily payment limit exceeded', count: 90 },
    { reason: 'Invalid OTP / Authentication failure', count: 60 },
  ];

  const failureData = failures.length > 0 ? failures : defaultFailures;

  const columns: Column<any>[] = [
    {
      key: 'transaction_code',
      header: 'Txn Reference',
      render: (row) => (
        <span className="font-mono text-xs font-semibold text-gray-800 bg-gray-100 px-2 py-0.5 rounded">
          {row.transaction_code}
        </span>
      ),
    },
    {
      key: 'transaction_date',
      header: 'Timestamp',
      render: (row) => (
        <span className="text-xs text-gray-500">{formatDateTime(row.transaction_date)}</span>
      ),
    },
    {
      key: 'amount',
      header: 'Amount',
      sortable: true,
      render: (row) => (
        <span className="font-bold text-gray-900">{formatCurrency(Number(row.amount))}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const colors: Record<string, string> = {
          success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          failed: 'bg-rose-50 text-rose-700 border-rose-200',
          pending: 'bg-amber-50 text-amber-700 border-amber-200',
          refunded: 'bg-blue-50 text-blue-700 border-blue-200',
        };
        return (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${
              colors[row.status] || 'bg-gray-50 text-gray-700'
            }`}
          >
            {row.status?.toUpperCase()}
          </span>
        );
      },
    },
    {
      key: 'payment_method',
      header: 'Instrument',
      render: (row) => (
        <span className="text-xs uppercase font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
          {row.payment_method}
        </span>
      ),
    },
    {
      key: 'gateway',
      header: 'Gateway',
      render: (row) => <span className="text-xs text-gray-600">{row.gateway || 'Razorpay'}</span>,
    },
    {
      key: 'failure_reason',
      header: 'Diagnosis / Reason',
      render: (row) => (
        <span className="text-xs text-red-600 font-medium truncate max-w-xs block">
          {row.failure_reason || '—'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <KPICard
          label="Total Txns"
          value={total}
          format="number"
          icon={CreditCard}
          subtitle="All attempted checkouts"
        />
        <KPICard
          label="Successful"
          value={successful}
          format="number"
          icon={CheckCircle2}
          subtitle="Cleared settlements"
        />
        <KPICard
          label="Failed"
          value={failed}
          format="number"
          icon={XCircle}
          subtitle="Gateway drops / declines"
        />
        <KPICard
          label="Success Rate"
          value={successRate}
          format="percentage"
          icon={CheckCircle2}
          subtitle="SLA threshold > 85%"
        />
        <KPICard
          label="Failure Rate"
          value={failureRate}
          format="percentage"
          icon={AlertTriangle}
          subtitle="Declined proportion"
        />
        <KPICard
          label="Average Ticket"
          value={avgValue}
          format="currency"
          icon={CreditCard}
          subtitle="Mean txn amount"
        />
      </div>

      {/* Failure Reason Breakdown Chart */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-900">Failure Reason Pareto Distribution</h3>
            <p className="text-xs text-gray-500">
              Root causes for unsettled payment attempts across gateways
            </p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 bg-red-50 text-red-700 rounded-full">
            Top Root Causes
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={failureData}
              layout="vertical"
              margin={{ top: 10, right: 20, left: 100, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis
                type="category"
                dataKey="reason"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                formatter={(val: any) => [val, 'Occurrences']}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Transaction Filter and DataTable */}
      <div className="space-y-4">
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center justify-between">
          <h3 className="text-sm font-bold text-gray-800">Transaction Audit Ledger</h3>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1">
              <Filter className="w-3.5 h-3.5 text-gray-500" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="text-xs font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
              >
                <option value="">All Statuses</option>
                <option value="success">Success</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            <div className="flex items-center space-x-1 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1">
              <select
                value={methodFilter}
                onChange={(e) => setMethodFilter(e.target.value)}
                className="text-xs font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
              >
                <option value="">All Instruments</option>
                <option value="upi">UPI</option>
                <option value="card">Card</option>
                <option value="netbanking">Netbanking</option>
                <option value="wallet">Wallet</option>
              </select>
            </div>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={transactions}
          total={totalTxns}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
        />
      </div>
    </div>
  );
};
