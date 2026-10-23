<template>
  <q-layout view="lHh Lpr lFf">
    <q-header><q-toolbar><q-toolbar-title>Espada Bank</q-toolbar-title><q-btn flat icon="logout" @click="logout" /></q-toolbar></q-header>
    <q-page-container><router-view /></q-page-container>
    <q-footer><q-tabs><q-route-tab to="/" icon="home" label="Home" /><q-route-tab to="/account" icon="account_balance_wallet" label="Account" /><q-route-tab to="/transactions" icon="receipt_long" label="Transactions" /></q-tabs></q-footer>
  </q-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import api from 'src/services/api'

const router = useRouter()
async function logout() {
  try { await api.post('/auth/logout') } finally {
    localStorage.removeItem('token')
    router.replace('/login')
  }
}
</script>
