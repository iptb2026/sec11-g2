<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">System Audit Logs</div>
        <div class="text-caption text-grey-7">Immutable security audit trails for regulatory compliance</div>
      </div>
      <q-btn color="secondary" icon="refresh" label="Refresh" outline @click="loadRows" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No audit logs recorded"
      >
        <template #body-cell-action_type="props">
          <q-td :props="props">
            <q-badge color="primary">{{ props.row.action_type }}</q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" align="center">
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const rows = ref([])
const loading = ref(false)

const columns = [
  { name: 'id', label: 'Log ID', field: 'id', sortable: true, align: 'left' },
  { name: 'action_type', label: 'Action Type', field: 'action_type', sortable: true, align: 'left' },
  { name: 'entity_name', label: 'Entity Target', field: 'entity_name', align: 'left' },
  { name: 'entity_id', label: 'Record ID', field: 'entity_id', align: 'left' },
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left' },
  { name: 'ip_address', label: 'IP Address', field: 'ip_address', align: 'left' },
  { name: 'action_timestamp', label: 'Timestamp', field: 'action_timestamp', format: val => val ? new Date(val).toLocaleString() : '', align: 'left' },
  { name: 'actions', label: 'Delete', field: 'actions', align: 'center' },
]

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/audit-logs/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load audit logs' })
  } finally {
    loading.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Purge',
    message: `Delete audit log record #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/audit-logs/${row.id}`)
      $q.notify({ type: 'positive', message: 'Audit log record deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(loadRows)
</script>
