import api from './client'

export const projectsApi = {
  list: (params?: any) => api.get('/projects', { params }),
  get: (id: number) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects', data),
  update: (id: number, data: any) => api.put(`/projects/${id}`, data),
  delete: (id: number) => api.delete(`/projects/${id}`),
  members: (id: number) => api.get(`/projects/${id}/members`),
  addMember: (id: number, userId: number, role: string) =>
    api.post(`/projects/${id}/members`, null, { params: { user_id: userId, role } }),
  removeMember: (id: number, userId: number) =>
    api.delete(`/projects/${id}/members/${userId}`),
}
