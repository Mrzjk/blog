import axios from 'axios'
import { useUserStore } from '../store/user'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const request = axios.create({
  baseURL,
  timeout: 10000
})

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

request.interceptors.response.use(
  response => response,
  error => {
    const userStore = useUserStore()
    if (error.response?.status === 401) {
      userStore.clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const wsBaseURL = (import.meta.env.VITE_WS_BASE_URL || baseURL.replace(/^http/, 'ws')).replace(/\/api\/v1$/, '')

export default request
