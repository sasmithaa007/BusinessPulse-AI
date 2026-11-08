import api from './axios';

export const revenueApi = {
  getSummary: (scenario: string) =>
    api.get(`/revenue/summary?scenario=${scenario}`),
  getTrend: (scenario: string) =>
    api.get(`/revenue/trend?scenario=${scenario}`),
  getLeakage: (scenario: string) =>
    api.get(`/revenue/leakage?scenario=${scenario}`),
};
