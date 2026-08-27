import { boot } from 'quasar/wrappers'
import api from 'src/services/api'
import { useAuthStore } from 'src/stores/auth-store'

export default boot(({ router }) => {
  api.interceptors.request.use((config) => {
    const token = useAuthStore().token
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  })
  api.interceptors.response.use((response) => response, (error) => {
    if (error.response?.status === 401) {
      useAuthStore().logout()
      router.push('/login')
    }
    return Promise.reject(error)
  })
})
