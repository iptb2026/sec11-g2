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
    googleChallenge: null,
    profilePhoto: null,
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
      if (data.otp_required || data.pin_required) return data
      await this.finishLogin(data)
      return { otp_required: false }
    },

    async verifyOtp (challengeToken, code) {
      const { data } = await api.post('/auth/otp/verify', { challenge_token: challengeToken, code })
      return data
    },

    async verifyPin (challengeToken, pin, confirmPin) {
      const { data } = await api.post('/auth/pin/verify', { challenge_token: challengeToken, pin, confirm_pin: confirmPin })
      await this.finishLogin(data)
    },

    async finishLogin (data) {
      if (!data.access_token) throw new Error('Sign-in could not be completed. Please try again.')
      this.token = data.access_token

      let me
      try { me = (await api.get('/auth/me')).data } catch (error) { this.token = null; throw error }

      this.userId = me.id
      this.username = me.username
      this.firstName = me.first_name
      this.lastName = me.last_name
      this.roleId = me.role_id

      this.roleCode = me.role_code
      this.roleName = me.role_name

      this.persist()
    },

    async logout (revoke = true) {
      const token = this.token
      this.token = null
      this.profilePhoto = null
      this.userId = null
      this.username = null
      this.firstName = null
      this.lastName = null
      this.roleId = null
      this.roleCode = null
      this.roleName = null
      localStorage.removeItem(STORAGE_KEY)
      if (revoke && token) {
        try { await api.post('/auth/logout', null, { headers: { Authorization: `Bearer ${token}` } }) } catch { /* The local session is already cleared. */ }
      }
    },
  },
})
