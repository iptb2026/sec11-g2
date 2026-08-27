<template>
  <div class="q-pa-md login-page-wrapper">
    <q-card class="login-card q-pa-md">
      <div class="login-avatar" aria-hidden="true">
        <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
          <circle cx="32" cy="30" r="16" fill="#fdeccf" />
          <path d="M10 28c4-10 18-14 22-9s10 6 14 9c0 0-2-12-14-16-14-4-22 6-22 16z" fill="#6172ee" />
          <path d="M8 56c6-8 20-8 24-8s18 0 24 8H8z" fill="#e6eef9" />
        </svg>
      </div>

      <div class="text-h5">Create your account</div>
      <p class="text-subtitle2">Register as a Velos customer.</p>

      <q-form @submit.prevent="submit">
        <q-input v-model="fullName" label="Full name" :rules="[val => !!val || 'Name required']" />
        <q-input v-model="email" label="Email" type="email" :rules="[val => !!val || 'Email required']" />
        <q-input v-model="password" label="Password" type="password" :rules="[val => val.length >= 6 || 'Use at least 6 characters']" />
        <q-input v-model="confirmPassword" label="Confirm password" type="password" :rules="[val => val === password || 'Passwords do not match']" />

        <q-btn class="full-width q-mt-md" label="Register" type="submit" color="primary" :loading="loading" />
      </q-form>

      <div class="text-center q-mt-md">
        <span>Already have an account?</span>
        <q-btn flat dense color="primary" label="Sign in" to="/login" />
      </div>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import * as authService from '@/services/authService'

const $q = useQuasar()
const router = useRouter()
const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await authService.register(fullName.value, email.value, password.value)
    $q.notify({ type: 'positive', message: 'Account created. Please sign in.' })
    router.push('/login')
  } catch (err) {
    const message = err?.data?.detail || 'Registration failed'
    $q.notify({ type: 'negative', message })
  } finally {
    loading.value = false
  }
}
</script>
