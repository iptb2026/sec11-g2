import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:5000/',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const persisted = localStorage.getItem('marquiso-auth')
  let token = null

  try {
    token = persisted ? JSON.parse(persisted).token : null
  } catch {
    localStorage.removeItem('marquiso-auth')
  }

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default api