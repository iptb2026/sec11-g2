import axios from 'axios'

const api = axios.create({ baseURL: process.env.QCLI_API_BASE_URL })

export function setApiBaseUrl(url) {
  api.defaults.baseURL = url.replace(/\/+$/, '')
}

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
