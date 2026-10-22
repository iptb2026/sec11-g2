<template>
  <div class="google-sign-in">
    <div class="login-divider"><span>or continue with</span></div>
    <div ref="button" class="google-button-host" :class="{ 'google-busy': busy }" />
    <p v-if="starting" class="google-status" role="status">Loading Google sign-in…</p>
    <p v-if="error" class="google-status" role="alert">{{ error }}</p>
    <q-form v-if="linkRequired" class="column q-gutter-sm q-mt-md" @submit="verify">
      <p class="google-status">An account already uses this email. Enter its password to connect Google.</p>
      <q-input v-model="password" type="password" autocomplete="current-password" label="Existing account password" filled :rules="[v => !!v || 'Enter your password']" />
      <q-btn type="submit" label="Connect Google and continue" color="primary" :loading="busy" />
    </q-form>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import api from '@/services/api'
const emit = defineEmits(['verified'])
const button = ref(null), error = ref(''), starting = ref(true), busy = ref(false), linkRequired = ref(false), password = ref('')
let nonce = '', credential = '', active = true
function loadGoogle () {
  if (window.google?.accounts?.id) return Promise.resolve()
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'; script.async = true
    const timeout = setTimeout(() => { script.remove(); reject(new Error('Google sign-in took too long to load. Reload the page to try again.')) }, 15000)
    script.onload = () => { clearTimeout(timeout); resolve() }
    script.onerror = () => { clearTimeout(timeout); script.remove(); reject(new Error('Could not load Google sign-in. Check your connection and reload the page.')) }
    document.head.appendChild(script)
  })
}
async function verify () {
  if (busy.value || !active) return
  busy.value = true; error.value = ''
  try {
    const { data } = await api.post('/auth/google/verify', { credential, nonce, password: password.value || undefined })
    if (!active) return
    if (data.password_required) linkRequired.value = true
    else { credential = ''; password.value = ''; emit('verified', data) }
  } catch (e) {
    error.value = typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Google sign-in could not be completed. Please try again.'
  } finally { busy.value = false }
}
onMounted(async () => {
  try {
    const { data } = await api.get('/auth/google/config')
    await loadGoogle()
    if (!active) return
    nonce = data.nonce
    window.google.accounts.id.initialize({ client_id: data.client_id, nonce, auto_select: false, callback: result => { if (active) { credential = result.credential; verify() } } })
    window.google.accounts.id.renderButton(button.value, { theme: 'filled_black', size: 'large', text: 'continue_with', shape: 'pill', width: Math.min(350, button.value.clientWidth) })
  } catch (e) {
    if (active) error.value = e.response?.status === 503 ? 'Google sign-in is not available yet. Please use email and password.' : 'Could not load Google sign-in. Please reload the page to retry.'
  } finally { starting.value = false }
})
onBeforeUnmount(() => { active = false; credential = ''; password.value = '' })
</script>
<style scoped>
.google-sign-in { margin-top: 28px; }
.login-divider { display: flex; align-items: center; gap: 10px; margin: 0 0 20px; color: #94a3ba; font-size: 12px; }
.login-divider::before, .login-divider::after { content: ''; flex: 1; height: 1px; background: #23303b; }
.google-button-host { display: flex; justify-content: center; min-height: 0; }
.google-busy { pointer-events: none; opacity: .6; }
.google-status { color: #a8b7ce; font-size: 13px; text-align: center; }
</style>
