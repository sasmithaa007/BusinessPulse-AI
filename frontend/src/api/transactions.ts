import api from './axios';

export const transactionsApi = {
  getTransactions: (params: {
    scenario: string;
    skip?: number;
    limit?: number;
    status?: string;
    payment_method?: string;
  }) => api.get('/transactions', { params }),
  getSummary: (scenario: string) =>
    api.get(`/transactions/summary?scenario=${scenario}`),
  getFailures: (scenario: string) =>
    api.get(`/transactions/failures?scenario=${scenario}`),
};
