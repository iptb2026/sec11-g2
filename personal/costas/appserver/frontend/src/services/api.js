import axios from 'axios'

export default axios.create({
  baseURL: import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:8000/'
})
