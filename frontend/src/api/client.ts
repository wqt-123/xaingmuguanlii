import axios from 'axios'

const api = axios.create({
  baseURL: '/qingtian/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('atlas-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem('atlas-token')
      sessionStorage.removeItem('atlas-user')
      window.location.href = '/qingtian/login'
    }
    return Promise.reject(err.response?.data || err)
  }
)

export default api
