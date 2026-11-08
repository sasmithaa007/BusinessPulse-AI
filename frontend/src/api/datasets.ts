import api from './axios';

export const datasetsApi = {
  upload: (formData: FormData) =>
    api.post('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getDatasets: () => api.get('/datasets'),
  getPreview: (id: string) => api.get(`/datasets/${id}/preview`),
};
