import { defineBoot } from '#q-app/wrappers'
import api from 'src/services/api'

export default defineBoot(({ router }) => {
  api.interceptors.response.use(response => response, error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.replace('/login')
    }
    return Promise.reject(error)
  })
})
