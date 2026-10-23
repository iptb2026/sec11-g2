<template>
  <q-page class="page q-pa-lg">
    <div class="text-h5 q-mb-md">My transactions</div>
    <q-list bordered separator>
      <q-item v-for="item in transactions" :key="item.id">
        <q-item-section><q-item-label>{{ item.transaction_type.replaceAll('_', ' ') }}</q-item-label><q-item-label caption>{{ new Date(item.transaction_date).toLocaleString() }}</q-item-label></q-item-section>
        <q-item-section side :class="item.credit_amount > 0 ? 'text-positive' : 'text-negative'">{{ item.credit_amount > 0 ? '+' : '-' }}{{ money(item.credit_amount > 0 ? item.credit_amount : item.debit_amount) }}</q-item-section>
      </q-item>
    </q-list>
    <div v-if="!loading && !transactions.length" class="text-grey-7 q-mt-md">No transactions found.</div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from 'src/services/api'

const transactions = ref([])
const loading = ref(true)
const money = value => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(value)
onMounted(async () => {
  try { transactions.value = (await api.get('/customer/transactions')).data } finally { loading.value = false }
})
</script>
