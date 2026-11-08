import React, { useEffect, useState } from 'react';
import { Search, Filter, X, ShieldAlert, CreditCard } from 'lucide-react';
import { useFilters } from '../hooks/useFilters';
import { customersApi } from '../api/customers';
import { DataTable, Column } from '../components/common/DataTable';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { formatCurrency, formatDate } from '../utils/formatters';

export const Customers: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [customers, setCustomers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [segment, setSegment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected customer for inspection drawer / modal
  const [selectedCustomer, setSelectedCustomer] = useState<any | null>(null);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await customersApi.getCustomers({
        scenario: scenarioKey,
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        status: status || undefined,
        segment: segment || undefined,
      });
      setCustomers(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load customer list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
  }, [scenarioKey, status, segment]);

  useEffect(() => {
    fetchCustomers();
  }, [scenarioKey, page, status, segment]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCustomers();
  };

  const columns: Column<any>[] = [
    {
      key: 'customer_code',
      header: 'Customer ID',
      render: (row) => (
        <span className="font-mono text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
          {row.customer_code}
        </span>
      ),
    },
    {
      key: 'name',
      header: 'Customer',
      sortable: true,
      render: (row) => (
        <div>
          <div className="font-semibold text-gray-900">{row.name}</div>
          <div className="text-xs text-gray-400">{row.email}</div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const colors: Record<string, string> = {
          active: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          inactive: 'bg-amber-50 text-amber-700 border-amber-200',
          churned: 'bg-rose-50 text-rose-700 border-rose-200',
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
      key: 'segment',
      header: 'Tier / Segment',
      render: (row) => (
        <span className="text-xs font-medium uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
          {row.segment}
        </span>
      ),
    },
    {
      key: 'lifetime_value',
      header: 'Historical LTV',
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-gray-900">
          {formatCurrency(Number(row.lifetime_value || 0))}
        </span>
      ),
    },
    {
      key: 'churn_risk_score',
      header: 'Churn Risk Propensity',
      render: (row) => {
        const score = Number(row.churn_risk_score || 0);
        const pct = Math.round(score * 100);
        const color =
          pct > 66 ? 'bg-red-500' : pct > 33 ? 'bg-amber-500' : 'bg-emerald-500';
        return (
          <div className="flex items-center space-x-2">
            <div className="w-16 bg-gray-200 rounded-full h-1.5 overflow-hidden">
              <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs font-mono font-medium text-gray-600">{pct}%</span>
          </div>
        );
      },
    },
    {
      key: 'signup_date',
      header: 'Joined Date',
      render: (row) => (
        <span className="text-xs text-gray-500">{formatDate(row.signup_date)}</span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setSelectedCustomer(row);
          }}
          className="text-xs font-semibold text-blue-600 hover:text-blue-800"
        >
          View Profile
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      {error && <ErrorMessage message={error} />}

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by customer name, code, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
          />
        </form>

        <div className="flex items-center space-x-2 w-full md:w-auto">
          <div className="flex items-center space-x-1 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1">
            <Filter className="w-3.5 h-3.5 text-gray-500" />
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="text-xs font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="churned">Churned</option>
            </select>
          </div>

          <div className="flex items-center space-x-1 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1">
            <select
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              className="text-xs font-medium text-gray-700 bg-transparent border-none focus:outline-none cursor-pointer"
            >
              <option value="">All Segments</option>
              <option value="basic">Basic</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <DataTable
        columns={columns}
        data={customers}
        loading={loading}
        total={total}
        page={page}
        pageSize={pageSize}
        onPageChange={(p) => setPage(p)}
        onRowClick={(row) => setSelectedCustomer(row)}
      />

      {/* Customer Inspector Drawer / Modal */}
      {selectedCustomer && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full shadow-2xl border border-gray-100 overflow-hidden flex flex-col">
            <div className="p-5 border-b border-gray-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm flex items-center justify-center">
                  {selectedCustomer.name?.charAt(0)}
                </div>
                <div>
                  <h3 className="text-base font-bold text-gray-900">{selectedCustomer.name}</h3>
                  <p className="text-xs text-gray-500 font-mono">
                    {selectedCustomer.customer_code} • {selectedCustomer.email}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCustomer(null)}
                className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <div className="text-[10px] uppercase font-semibold text-gray-400">Account Status</div>
                  <div className="text-sm font-bold text-gray-800 capitalize mt-0.5">
                    {selectedCustomer.status}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <div className="text-[10px] uppercase font-semibold text-gray-400">Customer Segment</div>
                  <div className="text-sm font-bold text-gray-800 capitalize mt-0.5">
                    {selectedCustomer.segment}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <div className="text-[10px] uppercase font-semibold text-gray-400">Cumulative Spend (LTV)</div>
                  <div className="text-sm font-bold text-blue-600 mt-0.5">
                    {formatCurrency(Number(selectedCustomer.lifetime_value || 0))}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                  <div className="text-[10px] uppercase font-semibold text-gray-400">Churn Risk Propensity</div>
                  <div className="text-sm font-bold text-gray-800 mt-0.5 flex items-center space-x-1.5">
                    <span>{Math.round(Number(selectedCustomer.churn_risk_score || 0) * 100)}%</span>
                    <span className="text-[10px] text-gray-400 font-normal">
                      (Logistic Regression)
                    </span>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-100 pt-4">
                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 flex items-center">
                  <CreditCard className="w-3.5 h-3.5 mr-1 text-gray-500" /> Account Meta
                </h4>
                <div className="text-xs text-gray-600 space-y-1">
                  <div>Joined on: <span className="font-semibold text-gray-800">{formatDate(selectedCustomer.signup_date)}</span></div>
                  <div>Scenario Context: <span className="font-semibold text-gray-800 uppercase">{selectedCustomer.business_scenario}</span></div>
                  <div>Jurisdiction: <span className="font-semibold text-gray-800">{selectedCustomer.country || 'India'}</span></div>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-end">
              <button
                onClick={() => setSelectedCustomer(null)}
                className="px-4 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-semibold rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
