import axios from 'axios'
import { normalizeServerUrl } from './server-url'

export const isNativeApp = Boolean(window.Capacitor?.isNativePlatform?.())

const api = axios.create({
  baseURL: isNativeApp && localStorage.getItem('bembankApiUrl')
    ? localStorage.getItem('bembankApiUrl')
    : import.meta.env.DEV
    ? '/bembank/api/'
    : import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:8000',
})

export function setApiBaseUrl (address) {
  const url = normalizeServerUrl(address)
  localStorage.setItem('bembankApiUrl', url)
  api.defaults.baseURL = url
}

// Never render validation objects or internal server details in customer forms.
api.interceptors.response.use(response => response, error => {
  if (error.response?.data && typeof error.response.data === 'object') {
    if (error.response.status >= 500) error.response.data.detail = 'This service is temporarily unavailable. Please try again.'
    else if (Array.isArray(error.response.data.detail)) error.response.data.detail = 'Some details are missing or invalid. Please check the form and try again.'
  }
  return Promise.reject(error)
})

export default api
