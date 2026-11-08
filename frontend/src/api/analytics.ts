import api from './axios';

export const analyticsApi = {
  getDashboardSummary: (scenario: string) =>
    api.get(`/dashboard/summary?scenario=${scenario}`),
  getRevenueTrend: (scenario: string) =>
    api.get(`/dashboard/revenue-trend?scenario=${scenario}`),
  getCustomerTrend: (scenario: string) =>
    api.get(`/dashboard/customer-trend?scenario=${scenario}`),
  getInsights: (scenario: string) =>
    api.get(`/insights?scenario=${scenario}`),
};
