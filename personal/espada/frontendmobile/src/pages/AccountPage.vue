<template>
  <q-page class="page q-pa-lg">
    <div class="text-h5 q-mb-md">My accounts</div>
    <q-card v-for="account in accounts" :key="account.id" class="q-mb-md">
      <q-card-section><div class="text-grey-7">{{ account.account_number }}</div><div class="balance">{{ money(account.available_balance) }}</div><q-badge :label="account.status" /></q-card-section>
    </q-card>
    <div v-if="!loading && !accounts.length" class="text-grey-7">No accounts found.</div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from 'src/services/api'

const accounts = ref([])
const loading = ref(true)
const money = value => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(value)
onMounted(async () => {
  try { accounts.value = (await api.get('/customer/accounts')).data } finally { loading.value = false }
})
</script>
