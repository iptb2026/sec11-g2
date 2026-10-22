const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`
  const headers = options.headers || {}

  const token = localStorage.getItem('auth_token')
  if (token) headers['Authorization'] = `Bearer ${token}`

  const opts = { headers, ...options }

  const res = await fetch(url, opts)

  if (res.status === 401) {
    // clear token and bubble up
    localStorage.removeItem('auth_token')
    throw { status: 401, message: 'Unauthorized' }
  }
  if (res.status === 403) {
    throw { status: 403, message: 'Forbidden' }
  }
  if (res.status === 204) return null

  const data = await res.json().catch(() => null)
  if (!res.ok) throw { status: res.status, data }
  return data
}

export async function postForm(path, form) {
  const body = new URLSearchParams(form)
  return request(path, { method: 'POST', body })
}

export async function get(path) {
  return request(path)
}

export async function post(path, payload) {
  return request(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
}

export async function put(path, payload) {
  return request(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
}

export async function del(path) {
  return request(path, { method: 'DELETE' })
}

export default { get, post, put, del, postForm }
