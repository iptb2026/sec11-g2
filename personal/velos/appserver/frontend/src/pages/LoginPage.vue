<template>
  <div class="login-page-wrapper">
    <div class="login-card">
      <section class="login-brand-panel">
        <div class="brand-mark">M</div>
        <div class="brand-name">Mini Bank</div>
        <h1>Money management<br />made personal.</h1>
        <p>Securely access your accounts and keep your everyday banking in one clear place.</p>
        <div class="brand-line"></div>
        <span class="brand-caption">Simple. Secure. Yours.</span>
      </section>

      <section class="login-form-panel">
        <div class="login-avatar" aria-hidden="true">
          <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" focusable="false">
            <circle cx="32" cy="30" r="16" fill="#fdeccf" />
            <path d="M10 28c4-10 18-14 22-9s10 6 14 9c0 0-2-12-14-16-14-4-22 6-22 16z" fill="#2d3b55" />
            <path d="M8 56c6-8 20-8 24-8s18 0 24 8H8z" fill="#d7e4f1" />
          </svg>
        </div>
        <div class="login-eyebrow">Welcome back</div>
        <div class="text-h5">Sign in to your account</div>
        <p class="login-subtitle">Enter your details to continue.</p>

        <q-form class="login-form" @submit.prevent="submit">
          <q-input v-model="email" outlined label="Email address" type="email" :rules="[val => !!val || 'Email required']" />
          <q-input v-model="password" outlined label="Password" :type="show ? 'text' : 'password'" :rules="[val => !!val || 'Password required']">
            <template v-slot:append>
              <q-icon :name="show ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="show = !show" />
            </template>
          </q-input>

          <div class="login-options">
            <q-checkbox v-model="remember" label="Remember me" />
            <q-btn flat dense label="Forgot password?" color="primary" disable />
          </div>
          <q-btn class="login-submit full-width" label="Sign in" type="submit" color="primary" :loading="loading" />
        </q-form>

        <div class="login-register">
          <span>New to Mini Bank?</span>
          <q-btn flat dense color="primary" label="Create account" to="/register" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuth } from '@/composables/useAuth'

const $q = useQuasar()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const show = ref(false)
const remember = ref(false)
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await login(email.value, password.value)
    $q.notify({ type: 'positive', message: 'Logged in' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Login failed' })
  } finally {
    loading.value = false
  }
}
</script>
