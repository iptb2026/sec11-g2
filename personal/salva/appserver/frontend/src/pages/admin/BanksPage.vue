<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Registered Banks</div>
        <div class="text-caption text-grey-7">Manage external partner banks for interbank clearing and transfers</div>
      </div>
      <q-btn color="primary" icon="add" label="New Bank" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No banks found"
      >
        <template #body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : 'grey'">
              {{ props.row.status }}
            </q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" class="q-gutter-xs">
            <q-btn flat round dense icon="edit" color="primary" @click="openEdit(props.row)" />
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 420px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Bank' : 'Register Bank' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.bank_code"
              label="Bank Code *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Bank code is required']"
            />
            <q-input
              v-model="form.bank_name"
              label="Bank Full Name *"
              filled
              :rules="[val => !!val || 'Bank name is required']"
            />
            <q-input
              v-model="form.swift_code"
              label="SWIFT / BIC Code"
              filled
            />
            <q-input
              v-model="form.short_name"
              label="Short Name / Acronym"
              filled
            />
            <q-select
              v-model="form.status"
              :options="['ACTIVE', 'INACTIVE']"
              label="Status *"
              filled
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Save'" :loading="saving" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const rows = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  bank_code: '',
  bank_name: '',
  swift_code: '',
  short_name: '',
  status: 'ACTIVE',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'bank_code', label: 'Bank Code', field: 'bank_code', sortable: true, align: 'left' },
  { name: 'bank_name', label: 'Bank Name', field: 'bank_name', sortable: true, align: 'left' },
  { name: 'short_name', label: 'Short Name', field: 'short_name', align: 'left' },
  { name: 'swift_code', label: 'SWIFT Code', field: 'swift_code', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/banks/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load banks' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    bank_code: '',
    bank_name: '',
    swift_code: '',
    short_name: '',
    status: 'ACTIVE',
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    bank_code: row.bank_code,
    bank_name: row.bank_name,
    swift_code: row.swift_code || '',
    short_name: row.short_name || '',
    status: row.status || 'ACTIVE',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/banks/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Bank updated' })
    } else {
      await api.post('/banks/', form.value)
      $q.notify({ type: 'positive', message: 'Bank registered' })
    }
    showDialog.value = false
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete bank "${row.bank_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/banks/${row.id}`)
      $q.notify({ type: 'positive', message: 'Bank deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(loadRows)
</script>
