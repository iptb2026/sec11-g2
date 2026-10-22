import { ref, computed } from 'vue'
import * as authService from '@/services/authService'

const currentUser = ref(null)
const isLoading = ref(false)

async function loadMe() {
  try {
    isLoading.value = true
    const data = await authService.me()
    currentUser.value = data
  } catch (err) {
    currentUser.value = null
  } finally {
    isLoading.value = false
  }
}

async function login(email, password) {
  isLoading.value = true
  try {
    await authService.login(email, password)
    await loadMe()
    // redirect based on role
    const role = currentUser.value?.role_code
    if (role === 'admin') window.location.hash = '#/admin/dashboard'
    else if (role === 'staff') window.location.hash = '#/staff/dashboard'
    else window.location.hash = '#/customer/dashboard'
    return true
  } catch (err) {
    throw err
  } finally {
    isLoading.value = false
  }
}

function logout() {
  authService.logout()
  currentUser.value = null
  window.location.hash = '#/login'
}

function hasRole(r) {
  return currentUser.value?.role_code === r
}

function can(roles) {
  if (!currentUser.value) return false
  return roles.includes(currentUser.value.role_code)
}

const isAuthenticated = computed(() => !!currentUser.value)

export function useAuth() {
  return {
    currentUser,
    isLoading,
    isAuthenticated,
    loadMe,
    login,
    logout,
    hasRole,
    can,
  }
}
