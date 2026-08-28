<template>
  <div class="login-page flex flex-center q-pa-md">
    <q-card class="login-card">
      <q-card-section class="login-heading">
        <p class="eyebrow">MARQUISO BANKING</p>
        <h1>{{ isRegistering ? 'Create account' : 'Sign in' }}</h1>
        <p>{{ isRegistering ? 'Register a secure customer account.' : 'Use your banking account to continue.' }}</p>
      </q-card-section>

      <q-card-section>
        <q-form class="q-gutter-md" @submit.prevent="isRegistering ? submitRegistration() : submitLogin()">
          <q-input
            v-model.trim="username"
            outlined
            label="Username"
            autocomplete="username"
            :disable="loading"
            :rules="[(value) => !!value || 'Username is required']"
          />
          <template v-if="isRegistering">
            <q-input v-model.trim="firstName" outlined label="First name" autocomplete="given-name" :disable="loading" :rules="[(value) => !!value || 'First name is required']" />
            <q-input v-model.trim="lastName" outlined label="Last name" autocomplete="family-name" :disable="loading" :rules="[(value) => !!value || 'Last name is required']" />
            <q-input v-model.trim="email" outlined type="email" label="Email" autocomplete="email" :disable="loading" :rules="[(value) => /.+@.+\..+/.test(value) || 'Enter a valid email']" />
          </template>
          <q-input
            v-model="password"
            outlined
            label="Password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            :disable="loading"
            :rules="[(value) => !!value || 'Password is required']"
          >
            <template #append>
              <q-icon
                class="cursor-pointer"
                :name="showPassword ? 'visibility_off' : 'visibility'"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>
          <q-input v-if="isRegistering" v-model="confirmPassword" outlined label="Confirm password" type="password" autocomplete="new-password" :disable="loading" :rules="[(value) => value === password || 'Passwords do not match']" />

          <q-banner v-if="error" rounded class="login-error">
            <template #avatar><q-icon name="error_outline" /></template>
            {{ error }}
          </q-banner>

          <q-btn
            class="full-width login-submit"
            color="primary"
            unelevated
            no-caps
            :label="isRegistering ? 'Create account' : 'Sign in'"
            type="submit"
            :loading="loading"
          />
          <q-btn flat class="full-width mode-button" color="primary" no-caps :label="isRegistering ? 'Already have an account? Sign in' : 'New customer? Create an account'" :disable="loading" @click="toggleMode" />
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const showPassword = ref(false)
const isRegistering = ref(false)
const loading = ref(false)
const error = ref('')

async function submitLogin () {
  loading.value = true
  error.value = ''

  try {
    await authStore.login(username.value, password.value)
    await router.push('/')
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || requestError.message || 'Sign in failed.'
  } finally {
    loading.value = false
  }
}

async function submitRegistration () {
  loading.value = true
  error.value = ''

  try {
    await api.post('/auth/register', {
      username: username.value,
      password: password.value,
      email: email.value,
      first_name: firstName.value,
      last_name: lastName.value,
      role_id: 3,
      account_status: 'ACTIVE',
    })
    await authStore.login(username.value, password.value)
    await router.push('/')
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || requestError.message || 'Registration failed.'
  } finally {
    loading.value = false
  }
}

function toggleMode () {
  isRegistering.value = !isRegistering.value
  error.value = ''
}

</script>

<style scoped>
.login-page { background: #f4f7f6; }
.login-card { width: min(100%, 430px); border: 1px solid #dce7e3; border-radius: 12px; box-shadow: 0 18px 50px rgba(24, 40, 39, 0.1); }
.login-heading { padding: 34px 34px 18px; }
.eyebrow { margin: 0 0 10px; color: #53746d; font-size: 11px; font-weight: 800; letter-spacing: 1.6px; }
h1 { margin: 0 0 8px; color: #182827; font-size: 2.2rem; line-height: 1; }
.login-heading p:last-child { margin: 0; color: #6b7c78; }
.login-error { color: #9e3737; background: #fff0ef; }
.login-submit { min-height: 46px; border-radius: 8px; }
.mode-button { min-height: 40px; }
</style>
