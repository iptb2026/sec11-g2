<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Audit Logs</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!--
      old_value / new_value are JSON fields on the backend, omitted here to keep
      this manual-entry form simple — they're normally filled in automatically
      when the app itself logs an action, not something typed by hand.
    -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">New Audit Log</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-select
            v-model="form.user_id"
            label="User"
            filled
            emit-value
            map-options
            :options="userOptions"
          />
          <q-input v-model="form.action_type" label="Action Type" filled hint="e.g. CREATE, UPDATE, DELETE" />
          <q-input v-model="form.entity_name" label="Entity Name" filled hint="e.g. users, accounts" />
          <q-input v-model.number="form.entity_id" label="Entity ID" type="number" filled />
          <q-input v-model="form.ip_address" label="IP Address" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left' },
  { name: 'action_type', label: 'Action', field: 'action_type', align: 'left' },
  { name: 'entity_name', label: 'Entity', field: 'entity_name', align: 'left' },
  { name: 'entity_id', label: 'Entity ID', field: 'entity_id', align: 'left' },
  { name: 'ip_address', label: 'IP Address', field: 'ip_address', align: 'left' },
  { name: 'action_timestamp', label: 'Timestamp', field: 'action_timestamp', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const userOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ user_id: null, action_type: '', entity_name: '', entity_id: null, ip_address: '' })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/audit-logs/')
  rows.value = data
  loading.value = false
}

async function loadUserOptions () {
  const { data } = await api.get('/users/')
  userOptions.value = data.map((u) => ({ label: u.username, value: u.id }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/audit-logs/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Audit log created' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete audit log #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/audit-logs/${row.id}`)
      $q.notify({ type: 'positive', message: 'Audit log deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadUserOptions()
})
</script>
