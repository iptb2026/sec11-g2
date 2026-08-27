import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    roleCode: (state) => state.user?.role_code || null,
    isAdmin: (state) => state.user?.role_code === 'ADMIN',
    isStaff: (state) => state.user?.role_code === 'STAFF',
    isCustomer: (state) => state.user?.role_code === 'CUSTOMER',
    fullName: (state) => {
      if (!state.user) return ''
      const parts = [state.user.first_name, state.user.middle_name, state.user.last_name].filter(Boolean)
      return parts.join(' ')
    },
  },

  actions: {
    async login(username, password) {
      // OAuth2PasswordRequestForm expects form-urlencoded
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)

      const { data } = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      this.token = data.access_token
      localStorage.setItem('token', data.access_token)

      // Fetch user profile
      await this.fetchMe()

      return this.user
    },

    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch (e) {
        // Ignore errors — we're clearing state anyway
      }
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
