import { defineStore } from 'pinia'
import api from '@/services/api'

const STORAGE_KEY = 'bank_auth'

function loadPersisted () {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const persisted = loadPersisted()

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: persisted?.token || null,
    userId: persisted?.userId || null,
    username: persisted?.username || null,
    firstName: persisted?.firstName || null,
    lastName: persisted?.lastName || null,
    roleId: persisted?.roleId || null,
    roleCode: persisted?.roleCode || null,
    roleName: persisted?.roleName || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    fullName: (state) => [state.firstName, state.lastName].filter(Boolean).join(' '),
    isAdmin: (state) => state.roleCode === 'ADMIN',
    isStaff: (state) => state.roleCode === 'STAFF',
    isCustomer: (state) => state.roleCode === 'CUSTOMER',
  },

  actions: {
    persist () {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        token: this.token,
        userId: this.userId,
        username: this.username,
        firstName: this.firstName,
        lastName: this.lastName,
        roleId: this.roleId,
        roleCode: this.roleCode,
        roleName: this.roleName,
      }))
    },

    async login (username, password) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)

      const { data } = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      this.token = data.access_token

      // No /auth/me endpoint exists on the backend, so the logged-in user's
      // own record (and therefore their role) is resolved client-side by
      // matching the username against the full user list.
      const { data: users } = await api.get('/users/')
      const me = users.find((u) => u.username === username)
      if (!me) {
        throw new Error('Logged in, but could not find a matching user record')
      }

      this.userId = me.id
      this.username = me.username
      this.firstName = me.first_name
      this.lastName = me.last_name
      this.roleId = me.role_id

      const { data: role } = await api.get(`/roles/${me.role_id}`)
      this.roleCode = role.role_code
      this.roleName = role.role_name

      this.persist()
    },

    logout () {
      this.token = null
      this.userId = null
      this.username = null
      this.firstName = null
      this.lastName = null
      this.roleId = null
      this.roleCode = null
      this.roleName = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
