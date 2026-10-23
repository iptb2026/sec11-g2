<template>
  <q-page class="flex flex-center q-pa-lg">
    <q-card class="full-width" style="max-width: 420px">
      <q-card-section><div class="text-h5">Espada Bank</div><div class="text-grey-7">Customer mobile banking</div></q-card-section>
      <q-form @submit="login">
        <q-card-section class="q-gutter-md">
          <q-input v-model="username" label="Username" outlined autocomplete="username" :rules="[v => !!v || 'Username is required']" />
          <q-input v-model="password" label="Password" outlined type="password" autocomplete="current-password" :rules="[v => !!v || 'Password is required']" />
          <q-banner v-if="error" dense class="bg-red-1 text-negative">{{ error }}</q-banner>
        </q-card-section>
        <q-card-actions><q-btn class="full-width" color="primary" label="Log in" type="submit" :loading="loading" /></q-card-actions>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from 'src/services/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  loading.value = true
  error.value = ''
  try {
    const body = new URLSearchParams({ username: username.value, password: password.value })
    const { data } = await api.post('/auth/login', body)
    localStorage.setItem('token', data.access_token)
    router.replace('/')
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Cannot connect to the server.'
  } finally { loading.value = false }
}
</script>
