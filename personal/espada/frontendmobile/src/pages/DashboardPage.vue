<template>
  <q-page class="page q-pa-lg">
    <div class="text-h5 q-mb-md">Hello, {{ user?.first_name || 'Customer' }}</div>
    <q-card><q-card-section><div class="text-grey-7">Total available balance</div><div class="balance">{{ money(total) }}</div></q-card-section></q-card>
    <q-banner v-if="error" class="q-mt-md bg-red-1 text-negative">{{ error }}</q-banner>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from 'src/services/api'

const user = ref(null)
const accounts = ref([])
const error = ref('')
const total = computed(() => accounts.value.reduce((sum, item) => sum + Number(item.available_balance), 0))
const money = value => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(value)

onMounted(async () => {
  try {
    const [me, accountList] = await Promise.all([api.get('/customer/me'), api.get('/customer/accounts')])
    user.value = me.data
    accounts.value = accountList.data
  } catch (requestError) { error.value = requestError.response?.data?.detail || 'Could not load your account.' }
})
</script>
