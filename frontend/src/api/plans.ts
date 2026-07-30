import api from './client'

export const plansApi = {
  list: (params?: any) => api.get('/plans', { params }),
  get: (id: number) => api.get(`/plans/${id}`),
  create: (data: any) => api.post('/plans', data),
  update: (id: number, data: any) => api.put(`/plans/${id}`, data),
  delete: (id: number) => api.delete(`/plans/${id}`),
  submit: (id: number) => api.post(`/plans/${id}/submit`),
  approve: (id: number) => api.post(`/plans/${id}/approve`),
}
