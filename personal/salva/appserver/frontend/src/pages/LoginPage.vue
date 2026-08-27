<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center bg-grey-2">
        <q-card style="width: 380px" bordered class="q-pa-md">
          <q-card-section class="text-center">
            <q-icon name="account_balance" size="48px" color="primary" />
            <div class="text-h5 text-weight-bold q-mt-sm">Salva Banking System</div>
            <div class="text-caption text-grey-7">Sign in to your account</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="onSubmit" class="column q-gutter-md">
              <q-input
                v-model="username"
                label="Username"
                filled
                autofocus
                :rules="[(val) => !!val || 'Username is required']"
              />
              <q-input
                v-model="password"
                label="Password"
                filled
                :type="showPassword ? 'text' : 'password'"
                :rules="[(val) => !!val || 'Password is required']"
              >
                <template #append>
                  <q-icon
                    :name="showPassword ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPassword = !showPassword"
                  />
                </template>
              </q-input>

              <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9" rounded>
                {{ errorMessage }}
              </q-banner>

              <q-btn
                type="submit"
                label="Log In"
                color="primary"
                class="full-width"
                :loading="loading"
                unelevated
              />
            </q-form>

            <div class="q-mt-lg text-caption text-grey-7 text-center">
              <div class="text-weight-bold q-mb-xs">Quick Demo Accounts:</div>
              <div class="row justify-center q-gutter-xs">
                <q-chip clickable dense outline color="purple" @click="username='admin'; password='1234'">
                  admin (Admin)
                </q-chip>
                <q-chip clickable dense outline color="blue-8" @click="username='mgarcia'; password='1234'">
                  mgarcia (Staff)
                </q-chip>
                <q-chip clickable dense outline color="teal" @click="username='jdelacruz'; password='1234'">
                  jdelacruz (Customer)
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const auth = useAuthStore()
const router = useRouter()

async function onSubmit () {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    if (err.response) {
      // Backend rejected the request (e.g. wrong credentials on /auth/login)
      errorMessage.value = err.response.data?.detail || `Login failed (HTTP ${err.response.status}).`
    } else if (err.request) {
      // Request never got a response at all: wrong API base URL, backend down, or CORS block
      errorMessage.value = 'Could not reach the backend API. Check that it is running and that the API base URL in .env is correct.'
    } else {
      // Something failed in our own post-login logic (e.g. no matching user record)
      errorMessage.value = err.message || 'Login failed for an unknown reason.'
    }
  } finally {
    loading.value = false
  }
}
</script>
