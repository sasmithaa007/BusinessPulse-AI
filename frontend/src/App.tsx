import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { FilterProvider } from './contexts/FilterContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';

// Auth Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ForgotPassword } from './pages/ForgotPassword';

// Application Pages
import { Dashboard } from './pages/Dashboard';
import { Customers } from './pages/Customers';
import { ChurnAnalysis } from './pages/ChurnAnalysis';
import { RetentionAnalysis } from './pages/RetentionAnalysis';
import { Segmentation } from './pages/Segmentation';
import { RevenueAnalytics } from './pages/RevenueAnalytics';
import { TransactionAnalytics } from './pages/TransactionAnalytics';
import { ProductAnalytics } from './pages/ProductAnalytics';
import { PerformanceAnalytics } from './pages/PerformanceAnalytics';
import { OperationsAnalytics } from './pages/OperationsAnalytics';
import { BusinessInsights } from './pages/BusinessInsights';
import { DatasetExplorer } from './pages/DatasetExplorer';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <FilterProvider>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Protected Enterprise Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/customers" element={<Customers />} />
                <Route path="/customers/churn" element={<ChurnAnalysis />} />
                <Route path="/customers/retention" element={<RetentionAnalysis />} />
                <Route path="/customers/segments" element={<Segmentation />} />
                <Route path="/revenue" element={<RevenueAnalytics />} />
                <Route path="/transactions" element={<TransactionAnalytics />} />
                <Route path="/products" element={<ProductAnalytics />} />
                <Route path="/performance" element={<PerformanceAnalytics />} />
                <Route path="/operations" element={<OperationsAnalytics />} />
                <Route path="/insights" element={<BusinessInsights />} />
                <Route path="/datasets" element={<DatasetExplorer />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
            </Route>

            {/* Catch-all redirects */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </FilterProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
