import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  CreditCard,
  Package,
  Gauge,
  Settings2,
  Lightbulb,
  Database,
  FileBarChart,
  Settings,
  ChevronDown,
  LogOut,
  BarChart3,
  UserCheck,
  UserX,
  PieChart,
} from 'lucide-react';
import { useAuthContext } from '../../contexts/AuthContext';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthContext();
  const navigate = useNavigate();
  const location = useLocation();

  const isCustomerRoute = location.pathname.startsWith('/customers');
  const [customersOpen, setCustomersOpen] = useState<boolean>(isCustomerRoute || true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItemClass = (isActive: boolean) =>
    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-blue-600 text-white shadow-sm'
        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
    }`;

  const subNavItemClass = (isActive: boolean) =>
    `flex items-center space-x-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
      isActive
        ? 'bg-blue-500/20 text-blue-400 font-semibold'
        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
    }`;

  return (
    <aside className="w-64 bg-[#0a1628] text-white flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md">
          <BarChart3 className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-base tracking-tight text-white block">
            BusinessPulse <span className="text-blue-400">AI</span>
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider block">
            Intelligence Platform
          </span>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        <NavLink to="/dashboard" className={({ isActive }) => navItemClass(isActive)}>
          <LayoutDashboard className="w-4 h-4" />
          <span>Dashboard</span>
        </NavLink>

        {/* Customers Collapsible */}
        <div>
          <button
            onClick={() => setCustomersOpen(!customersOpen)}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isCustomerRoute && !customersOpen
                ? 'bg-blue-600/30 text-blue-300'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center space-x-3">
              <Users className="w-4 h-4" />
              <span>Customers</span>
            </div>
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-200 ${
                customersOpen ? 'rotate-180 text-blue-400' : 'text-slate-400'
              }`}
            />
          </button>

          {customersOpen && (
            <div className="mt-1 ml-4 pl-3 border-l border-slate-800 space-y-1">
              <NavLink to="/customers" end className={({ isActive }) => subNavItemClass(isActive)}>
                <Users className="w-3.5 h-3.5" />
                <span>Customer Directory</span>
              </NavLink>
              <NavLink to="/customers/churn" className={({ isActive }) => subNavItemClass(isActive)}>
                <UserX className="w-3.5 h-3.5" />
                <span>Churn Analysis</span>
              </NavLink>
              <NavLink to="/customers/retention" className={({ isActive }) => subNavItemClass(isActive)}>
                <UserCheck className="w-3.5 h-3.5" />
                <span>Retention & Cohorts</span>
              </NavLink>
              <NavLink to="/customers/segments" className={({ isActive }) => subNavItemClass(isActive)}>
                <PieChart className="w-3.5 h-3.5" />
                <span>Segmentation & RFM</span>
              </NavLink>
            </div>
          )}
        </div>

        <NavLink to="/revenue" className={({ isActive }) => navItemClass(isActive)}>
          <TrendingUp className="w-4 h-4" />
          <span>Revenue & Leakage</span>
        </NavLink>

        <NavLink to="/transactions" className={({ isActive }) => navItemClass(isActive)}>
          <CreditCard className="w-4 h-4" />
          <span>Transactions</span>
        </NavLink>

        <NavLink to="/products" className={({ isActive }) => navItemClass(isActive)}>
          <Package className="w-4 h-4" />
          <span>Product Usage</span>
        </NavLink>

        <NavLink to="/performance" className={({ isActive }) => navItemClass(isActive)}>
          <Gauge className="w-4 h-4" />
          <span>API Performance</span>
        </NavLink>

        <NavLink to="/operations" className={({ isActive }) => navItemClass(isActive)}>
          <Settings2 className="w-4 h-4" />
          <span>Operations & SLAs</span>
        </NavLink>

        <NavLink to="/insights" className={({ isActive }) => navItemClass(isActive)}>
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span>AI Insights</span>
        </NavLink>

        <div className="pt-3 pb-1">
          <div className="px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            Data & Tools
          </div>
        </div>

        <NavLink to="/datasets" className={({ isActive }) => navItemClass(isActive)}>
          <Database className="w-4 h-4" />
          <span>Datasets</span>
        </NavLink>

        <NavLink to="/reports" className={({ isActive }) => navItemClass(isActive)}>
          <FileBarChart className="w-4 h-4" />
          <span>Reports & Export</span>
        </NavLink>

        <NavLink to="/settings" className={({ isActive }) => navItemClass(isActive)}>
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>
      </nav>

      {/* User Footer */}
      <div className="p-4 border-t border-slate-800 bg-[#081220]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-blue-600/30 border border-blue-500/50 flex items-center justify-center font-bold text-xs text-blue-300">
              {user?.fullName?.charAt(0) || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-white truncate">
                {user?.fullName || 'Analyst'}
              </p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
