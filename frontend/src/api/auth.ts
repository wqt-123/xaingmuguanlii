import api from './client'

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (data: { username: string; password: string; name: string; email?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}
