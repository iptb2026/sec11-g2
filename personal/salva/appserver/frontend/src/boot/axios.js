import { boot } from 'quasar/wrappers'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

export default boot(({ app, router }) => {
  api.interceptors.request.use((config) => {
    const auth = useAuthStore()
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        const auth = useAuthStore()
        auth.logout()
        router.push('/login')
      }
      return Promise.reject(error)
    }
  )

  app.config.globalProperties.$api = api
})

export { api }
