import api from './api'

export async function login(email, password) {
  // backend expects OAuth2 form with username & password
  const data = await api.postForm('/auth/login', { username: email, password })
  if (data && data.access_token) {
    localStorage.setItem('auth_token', data.access_token)
  }
  return data
}

export async function register(fullName, email, password) {
  return api.post('/auth/register', { full_name: fullName, email, password })
}

export function logout() {
  localStorage.removeItem('auth_token')
}

export async function me() {
  return api.get('/users/me')
}

export default { login, register, logout, me }
