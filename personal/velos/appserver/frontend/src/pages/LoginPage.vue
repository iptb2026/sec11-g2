<template>
  <div class="q-pa-md login-page-wrapper">
    <q-card class="login-card q-pa-md">
      <div class="login-avatar">
        <!-- Simple user head with hair SVG illustration -->
        <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
          <defs>
            <linearGradient id="g1" x1="0" x2="1">
              <stop offset="0" stop-color="#6b7cff" />
              <stop offset="1" stop-color="#52d0ff" />
            </linearGradient>
          </defs>
          <circle cx="32" cy="30" r="16" fill="#fdeccf" />
          <!-- hair -->
          <path d="M10 28c4-10 18-14 22-9s10 6 14 9c0 0-2-12-14-16-14-4-22 6-22 16z" fill="url(#g1)" />
          <!-- torso/shoulders -->
          <path d="M8 56c6-8 20-8 24-8s18 0 24 8v0H8z" fill="#e6eef9" />
        </svg>
      </div>

      <div class="text-h5">Mini Bank — Sign in</div>

      <q-form @submit.prevent="submit">
        <q-input v-model="email" label="Email" type="email" :rules="[val => !!val || 'Email required']" />
        <q-input v-model="password" label="Password" :type="show ? 'text' : 'password'" :rules="[val => !!val || 'Password required']">
          <template v-slot:append>
            <q-icon :name="show ? 'visibility_off' : 'visibility'" class="cursor-pointer" @click="show = !show" />
          </template>
        </q-input>

        <div class="row items-center q-gutter-sm">
          <q-checkbox v-model="remember" label="Remember me" />
          <q-btn label="Login" type="submit" color="primary" :loading="loading" />
        </div>
      </q-form>

      <div class="text-center q-mt-md">
        <span>New to Velos?</span>
        <q-btn flat dense color="primary" label="Create account" to="/register" />
      </div>
    </q-card>
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
