<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Fee Types</div>
        <div class="text-caption text-grey-7">Configure banking service fees, maintenance charges, and rates</div>
      </div>
      <q-btn color="primary" icon="add" label="New Fee Type" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No fee types found"
      >
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
          <div class="text-h6">{{ editingId ? 'Edit Fee Type' : 'Create Fee Type' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.fee_code"
              label="Fee Code *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Fee code is required']"
            />
            <q-input
              v-model="form.fee_name"
              label="Fee Name *"
              filled
              :rules="[val => !!val || 'Fee name is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.fixed_amount"
                  label="Fixed Amount (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model.number="form.percentage_rate"
                  label="Rate (e.g. 0.01) *"
                  type="number"
                  step="0.001"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
            </div>
            <q-input
              v-model="form.fee_description"
              label="Description"
              type="textarea"
              filled
              rows="3"
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
  fee_code: '',
  fee_name: '',
  fee_description: '',
  fixed_amount: 0,
  percentage_rate: 0,
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'fee_code', label: 'Code', field: 'fee_code', sortable: true, align: 'left' },
  { name: 'fee_name', label: 'Fee Name', field: 'fee_name', sortable: true, align: 'left' },
  { name: 'fixed_amount', label: 'Fixed Amount', field: 'fixed_amount', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'percentage_rate', label: 'Percentage', field: 'percentage_rate', format: val => `${(Number(val) * 100).toFixed(2)}%`, align: 'right' },
  { name: 'fee_description', label: 'Description', field: 'fee_description', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/fee-types/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load fee types' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    fee_code: '',
    fee_name: '',
    fee_description: '',
    fixed_amount: 50,
    percentage_rate: 0,
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    fee_code: row.fee_code,
    fee_name: row.fee_name,
    fee_description: row.fee_description || '',
    fixed_amount: Number(row.fixed_amount),
    percentage_rate: Number(row.percentage_rate),
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/fee-types/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Fee type updated' })
    } else {
      await api.post('/fee-types/', form.value)
      $q.notify({ type: 'positive', message: 'Fee type created' })
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
    message: `Delete fee type "${row.fee_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/fee-types/${row.id}`)
      $q.notify({ type: 'positive', message: 'Fee type deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(loadRows)
</script>
