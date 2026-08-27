<template>
  <q-layout view="hHh lpR fFf" class="login-bg">
    <q-page-container>
      <q-page class="flex flex-center">
        <q-card class="login-card q-pa-lg" style="width: 420px; max-width: 95vw">
          <q-card-section class="text-center q-pb-none">
            <q-icon name="account_balance" size="48px" color="primary" />
            <div class="text-h5 q-mt-sm text-weight-bold text-primary">
              Mini Banking System
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">
              Sign in to your account
            </div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="handleLogin" class="q-gutter-md">
              <q-input
                v-model="username"
                label="Username"
                outlined
                dense
                :rules="[val => !!val || 'Username is required']"
                id="login-username"
              >
                <template v-slot:prepend>
                  <q-icon name="person" />
                </template>
              </q-input>

              <q-input
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                outlined
                dense
                :rules="[val => !!val || 'Password is required']"
                id="login-password"
              >
                <template v-slot:prepend>
                  <q-icon name="lock" />
                </template>
                <template v-slot:append>
                  <q-icon
                    :name="showPassword ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPassword = !showPassword"
                  />
                </template>
              </q-input>

              <q-banner v-if="errorMsg" dense class="bg-negative text-white q-mb-sm" rounded>
                <template v-slot:avatar>
                  <q-icon name="error" />
                </template>
                {{ errorMsg }}
              </q-banner>

              <q-btn
                type="submit"
                label="Sign In"
                color="primary"
                class="full-width"
                size="md"
                :loading="loading"
                id="login-submit"
                unelevated
              />
            </q-form>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''

  try {
    const user = await auth.login(username.value, password.value)
    const role = user.role_code

    if (role === 'ADMIN') router.push('/admin/dashboard')
    else if (role === 'STAFF') router.push('/staff/dashboard')
    else if (role === 'CUSTOMER') router.push('/customer/dashboard')
    else router.push('/login')
  } catch (err) {
    const detail = err.response?.data?.detail
    errorMsg.value = detail || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-bg {
  background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
  min-height: 100vh;
}
.login-card {
  border-radius: 12px;
}
</style>
