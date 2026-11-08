import React from 'react';
import { useLocation } from 'react-router-dom';
import { Layers, Bell, RefreshCw, ShieldAlert } from 'lucide-react';
import { useFilters, Scenario } from '../../hooks/useFilters';
import { DateFilter } from '../common/DateFilter';

export const Header: React.FC = () => {
  const { scenario, setScenario } = useFilters();
  const location = useLocation();

  const getPageTitle = (path: string): string => {
    switch (path) {
      case '/dashboard':
        return 'Executive Dashboard';
      case '/customers':
        return 'Customer Analytics & Directory';
      case '/customers/churn':
        return 'Customer Churn Intelligence';
      case '/customers/retention':
        return 'Retention & Cohort Analysis';
      case '/customers/segments':
        return 'Customer Segmentation & RFM';
      case '/revenue':
        return 'Revenue Analytics & Leakage';
      case '/transactions':
        return 'Transaction Health & Gateway Metrics';
      case '/products':
        return 'Product Usage & Feature Adoption';
      case '/performance':
        return 'API Performance & Latency Telemetry';
      case '/operations':
        return 'Operational Efficiency & Bottlenecks';
      case '/insights':
        return 'AI Business Insights & Actions';
      case '/datasets':
        return 'Dataset Management & Hygiene';
      case '/reports':
        return 'Business Reports & CSV Exports';
      case '/settings':
        return 'Platform Settings';
      default:
        return 'BusinessPulse AI';
    }
  };

  const scenarioColors: Record<Scenario, string> = {
    FinTech: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    SaaS: 'bg-blue-50 text-blue-700 border-blue-200',
    'Developer Tools': 'bg-purple-50 text-purple-700 border-purple-200',
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Title */}
      <div className="flex items-center space-x-4">
        <h1 className="text-lg font-bold text-gray-900 tracking-tight">
          {getPageTitle(location.pathname)}
        </h1>

        {/* Synthetic Data Alert Badge */}
        <span className="hidden md:inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
          <ShieldAlert className="w-3 h-3 text-amber-600 mr-1" />
          SYNTHETIC DATA (SEED 42)
        </span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Scenario Switcher */}
        <div className="flex items-center space-x-1.5 bg-gray-50 border border-gray-200 rounded-lg p-1">
          <Layers className="w-4 h-4 text-gray-500 ml-1.5" />
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value as Scenario)}
            className={`text-xs font-semibold rounded-md px-2 py-1 border transition-colors cursor-pointer ${scenarioColors[scenario]}`}
          >
            <option value="FinTech">FinTech Scenario</option>
            <option value="SaaS">SaaS Scenario</option>
            <option value="Developer Tools">Developer Tools</option>
          </select>
        </div>

        {/* Date Filter */}
        <DateFilter />

        {/* Notifications and Action */}
        <button
          onClick={() => window.location.reload()}
          title="Reload data"
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        <button
          title="Notifications"
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition relative"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full"></span>
        </button>
      </div>
    </header>
  );
};
