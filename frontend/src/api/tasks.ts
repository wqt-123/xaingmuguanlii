import api from './client'

export const tasksApi = {
  list: (params?: any) => api.get('/tasks', { params }),
  my: () => api.get('/tasks/my'),
  get: (id: number) => api.get(`/tasks/${id}`),
  create: (data: any) => api.post('/tasks', data),
  update: (id: number, data: any) => api.put(`/tasks/${id}`, data),
  delete: (id: number) => api.delete(`/tasks/${id}`),
  updateStatus: (id: number, status: string) => api.patch(`/tasks/${id}/status`, { status }),
  move: (id: number, data: any) => api.put(`/tasks/${id}/move`, data),
  ganttData: (planId: number) => api.get(`/tasks/gantt/${planId}`),
}
