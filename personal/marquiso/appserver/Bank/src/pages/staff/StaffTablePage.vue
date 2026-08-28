<template>
  <q-page class="staff-page q-pa-md q-pa-lg-xl">
    <div class="staff-shell">
      <p class="eyebrow">STAFF OPERATIONS</p>
      <div class="page-heading">
        <div><h1>{{ title }}</h1><p>{{ description }}</p></div>
        <q-btn color="primary" unelevated no-caps icon="refresh" label="Refresh" :loading="loading" @click="loadData" />
      </div>
      <q-banner v-if="error" rounded class="error-banner"><template #avatar><q-icon name="error_outline" /></template>{{ error }}</q-banner>
      <q-table flat bordered row-key="id" :rows="rows" :columns="columns" :loading="loading" no-data-label="No records found" class="staff-table">
        <template #body-cell-transfer_fee="props"><q-td :props="props">PHP {{ props.value || '0.00' }}</q-td></template>
      </q-table>
    </div>
  </q-page>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import api from '@/services/api'
const props = defineProps({ title: { type: String, required: true }, description: { type: String, required: true }, endpoint: { type: String, required: true }, columns: { type: Array, required: true } })
const rows = ref([])
const loading = ref(false)
const error = ref('')
async function loadData () {
  loading.value = true
  error.value = ''
  try { const { data } = await api.get(props.endpoint); rows.value = Array.isArray(data) ? data : [] } catch (requestError) { error.value = requestError.response?.data?.detail || 'Unable to load staff data.' } finally { loading.value = false }
}
onMounted(loadData)
</script>
<style scoped>
.staff-page { background: #f4f7f6; color: #182827; }
.staff-shell { max-width: 1180px; margin: 0 auto; }
.eyebrow { margin: 28px 0 8px; color: #53746d; font-size: 11px; font-weight: 800; letter-spacing: 1.6px; }
.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 24px; }
h1 { margin: 0 0 8px; font-size: 2.4rem; line-height: 1; }
.page-heading p { margin: 0; color: #71817d; }
.staff-table { border-radius: 10px; background: #fff; }
.error-banner { margin-bottom: 16px; color: #9e3737; background: #fff0ef; }
@media (max-width: 600px) { .page-heading { align-items: stretch; flex-direction: column; } }
</style>
