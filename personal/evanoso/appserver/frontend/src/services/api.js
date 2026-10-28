import axios from 'axios'
import { savedApiUrl } from '@/utils/api-url'

const api = axios.create({
  baseURL: import.meta.env.DEV
    ? '/bembank/api/'
    : savedApiUrl() || import.meta.env.QCLI_API_BASE_URL || '/api/',
})

// Never render validation objects or internal server details in customer forms.
api.interceptors.response.use(response => response, error => {
  if (error.response?.data && typeof error.response.data === 'object') {
    if (error.response.status >= 500) error.response.data.detail = 'This service is temporarily unavailable. Please try again.'
    else if (Array.isArray(error.response.data.detail)) error.response.data.detail = 'Some details are missing or invalid. Please check the form and try again.'
  }
  return Promise.reject(error)
})

export default api
