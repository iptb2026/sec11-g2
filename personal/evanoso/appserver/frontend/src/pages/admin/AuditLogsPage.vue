<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Audit Logs</div>
      <q-space />
      <q-btn flat icon="refresh" label="Refresh" @click="loadRows" :loading="loading" />
    </div>

    <q-banner v-if="errorMessage" class="bank-feedback q-mb-md">{{ errorMessage }}<template #action><q-btn flat label="Retry" @click="loadRows" /></template></q-banner>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered :pagination="{ sortBy: 'action_timestamp', descending: true, rowsPerPage: 10 }" />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
const errorMessage = ref('')
const currency = new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' })
function details (value) {
  if (typeof value === 'string') { try { value = JSON.parse(value) } catch { return {} } }
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
}
function amount (row) {
  const after = details(row.new_value), before = details(row.old_value)
  const value = after.amount ?? after.opening_balance ?? before.amount ?? before.opening_balance
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) ? currency.format(Number(value)) : '—'
}
const title = value => String(value || '—').replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left' },
  { name: 'action_type', label: 'Action', field: 'action_type', format: title, align: 'left' },
  { name: 'entity_name', label: 'Activity', field: 'entity_name', format: value => value === 'presentation_demo_v1' ? 'Account setup' : title(value), align: 'left' },
  { name: 'entity_id', label: 'Entity ID', field: 'entity_id', align: 'left' },
  { name: 'amount', label: 'Amount', field: amount, align: 'right' },
  { name: 'action_timestamp', label: 'Date & time', field: 'action_timestamp', sortable: true, format: value => { const date = new Date(value); return value && !Number.isNaN(date.getTime()) ? date.toLocaleString('en-PH', { timeZone: 'Asia/Manila', dateStyle: 'medium', timeStyle: 'short' }) : '—' }, align: 'left' },
]

const rows = ref([])
const loading = ref(false)

async function loadRows () {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get('/audit-logs/')
    rows.value = data
  } catch {
    errorMessage.value = 'Activity could not be loaded. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadRows)
</script>
