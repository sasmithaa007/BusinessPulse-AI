import React, { useState } from 'react';
import {
  User,
  Settings as SettingsIcon,
  Database,
  Code,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { useAuthContext } from '../contexts/AuthContext';
import { useFilters, Scenario } from '../hooks/useFilters';

export const Settings: React.FC = () => {
  const { user } = useAuthContext();
  const { scenario, setScenario } = useFilters();

  const [activeTab, setActiveTab] = useState<'profile' | 'app' | 'demo' | 'api'>('profile');
  const [savedMessage, setSavedMessage] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 space-x-6 text-sm font-semibold">
        <button
          onClick={() => setActiveTab('profile')}
          className={`pb-3 flex items-center space-x-2 transition-colors ${
            activeTab === 'profile'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          <User className="w-4 h-4" />
          <span>Profile</span>
        </button>

        <button
          onClick={() => setActiveTab('app')}
          className={`pb-3 flex items-center space-x-2 transition-colors ${
            activeTab === 'app'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          <SettingsIcon className="w-4 h-4" />
          <span>Platform Config</span>
        </button>

        <button
          onClick={() => setActiveTab('demo')}
          className={`pb-3 flex items-center space-x-2 transition-colors ${
            activeTab === 'demo'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Synthetic Data</span>
        </button>

        <button
          onClick={() => setActiveTab('api')}
          className={`pb-3 flex items-center space-x-2 transition-colors ${
            activeTab === 'api'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-800'
          }`}
        >
          <Code className="w-4 h-4" />
          <span>API & Swagger</span>
        </button>
      </div>

      {savedMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold p-3 rounded-lg flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Configuration saved successfully.</span>
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-6">
          <h3 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3">
            Analyst Profile & Access Tier
          </h3>

          <form onSubmit={handleSave} className="space-y-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Full Name
              </label>
              <input
                type="text"
                defaultValue={user?.fullName || 'Demo Administrator'}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Email Address
              </label>
              <input
                type="email"
                disabled
                defaultValue={user?.email || 'admin@businesspulse.demo'}
                className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-500 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Assigned Role
              </label>
              <input
                type="text"
                disabled
                defaultValue={user?.role?.toUpperCase() || 'ADMIN'}
                className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-500 cursor-not-allowed uppercase font-mono"
              />
            </div>

            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
            >
              Update Preferences
            </button>
          </form>
        </div>
      )}

      {/* App Config Tab */}
      {activeTab === 'app' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-6">
          <h3 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3">
            Business Intelligence Defaults
          </h3>

          <div className="space-y-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Active Scenario Focus
              </label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value as Scenario)}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm font-semibold text-gray-800"
              >
                <option value="FinTech">FinTech (Groww / Zerodha / Juspay style)</option>
                <option value="SaaS">SaaS (Chargebee / Avalara style)</option>
                <option value="Developer Tools">Developer Tools (Postman / BrowserStack style)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Display Currency
              </label>
              <input
                type="text"
                disabled
                value="Indian Rupee (₹ INR) — Fixed for Demo Portfolio"
                className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-600 cursor-not-allowed font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                Dashboard Theme
              </label>
              <input
                type="text"
                disabled
                value="Enterprise Light (Dark Navy Navigation)"
                className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-600 cursor-not-allowed font-medium"
              />
            </div>
          </div>
        </div>
      )}

      {/* Demo Data Tab */}
      {activeTab === 'demo' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-5">
          <h3 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3">
            Synthetic Seed Governance (Seed 42)
          </h3>

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-2">
            <div className="flex items-center space-x-2 font-bold">
              <ShieldCheck className="w-4 h-4 text-amber-700" />
              <span>Interview & Regulatory Compliance Disclosure</span>
            </div>
            <p className="leading-relaxed">
              All records, entity names, transactions, and logs are 100% synthetically generated
              using deterministic pseudo-random generators (`seed=42`). No proprietary company
              data or PII is contained within this repository.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">Target Customers</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">5,000</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">Target Transactions</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">20,000</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">Target Subscriptions</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">5,000</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">Usage Events</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">15,000</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">API Logs</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">20,000</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400">Operational Records</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">5,000</div>
            </div>
          </div>
        </div>
      )}

      {/* API Info Tab */}
      {activeTab === 'api' && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
          <h3 className="text-base font-bold text-gray-900 border-b border-gray-100 pb-3">
            FastAPI OpenAPI Specification & Swagger UI
          </h3>

          <p className="text-xs text-gray-600 leading-relaxed">
            The backend exposes auto-generated interactive OpenAPI documentation. You can test
            authentication, analytical endpoints, and CSV exports directly from Swagger:
          </p>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div className="font-mono text-xs text-slate-800">
              http://localhost:8000/docs
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs font-bold text-blue-600 hover:text-blue-800"
            >
              <span>Launch Swagger UI</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div className="font-mono text-xs text-slate-800">
              http://localhost:8000/redoc
            </div>
            <a
              href="http://localhost:8000/redoc"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs font-bold text-blue-600 hover:text-blue-800"
            >
              <span>Launch ReDoc</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      )}
    </div>
  );
};
