import { defineStore } from 'pinia'
import api from 'src/services/api'

const STORAGE_KEY = 'bank_auth'
const load = () => {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') } catch { return {} }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: load().token || null, username: load().username || '', userId: load().userId || null, roleCode: load().roleCode || '' }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    isAdmin: (state) => state.roleCode === 'ADMIN',
    isStaff: (state) => state.roleCode === 'STAFF',
    isCustomer: (state) => state.roleCode === 'CUSTOMER'
  },
  actions: {
    persist () { localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: this.token, username: this.username, userId: this.userId, roleCode: this.roleCode })) },
    async login (username, password) {
      const form = new URLSearchParams({ username, password })
      const { data: token } = await api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      this.token = token.access_token
      this.username = username
      const { data: users } = await api.get('/users/')
      const user = users.find((item) => item.username === username)
      if (!user) throw new Error('Logged-in user was not found')
      this.userId = user.id
      const { data: role } = await api.get(`/roles/${user.role_id}`)
      this.roleCode = role.role_code
      this.persist()
    },
    logout () {
      this.token = null; this.username = ''; this.userId = null; this.roleCode = ''
      localStorage.removeItem(STORAGE_KEY)
    }
  }
})
