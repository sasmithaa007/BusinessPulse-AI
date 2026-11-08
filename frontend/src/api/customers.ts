import api from './axios';

export const customersApi = {
  getCustomers: (params: {
    scenario: string;
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
    segment?: string;
  }) => api.get('/customers', { params }),
  getCustomerById: (id: string | number) => api.get(`/customers/${id}`),
  getChurnOverview: (scenario: string) =>
    api.get(`/customers/churn?scenario=${scenario}`),
  getChurnTrend: (scenario: string) =>
    api.get(`/customers/churn/trend?scenario=${scenario}`),
  getChurnPrediction: (scenario: string) =>
    api.get(`/customers/churn/prediction?scenario=${scenario}`),
  getRetentionOverview: (scenario: string) =>
    api.get(`/customers/retention?scenario=${scenario}`),
  getRetentionCohort: (scenario: string) =>
    api.get(`/customers/retention/cohort?scenario=${scenario}`),
  getRetentionBySegment: (scenario: string) =>
    api.get(`/customers/retention/by-segment?scenario=${scenario}`),
  getSegmentsDistribution: (scenario: string) =>
    api.get(`/customers/segments?scenario=${scenario}`),
  getSegmentsRFM: (scenario: string) =>
    api.get(`/customers/segments/rfm?scenario=${scenario}`),
};
