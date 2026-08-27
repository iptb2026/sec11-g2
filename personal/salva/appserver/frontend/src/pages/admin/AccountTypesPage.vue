<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Account Types</div>
        <div class="text-caption text-grey-7">Configure banking account products, minimum balances, and interest rates</div>
      </div>
      <q-btn color="primary" icon="add" label="New Account Type" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No account types found"
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
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Account Type' : 'Create Account Type' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.type_code"
              label="Type Code *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Type code is required']"
            />
            <q-input
              v-model="form.type_name"
              label="Type Name *"
              filled
              :rules="[val => !!val || 'Type name is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.minimum_balance"
                  label="Min Balance (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model.number="form.opening_deposit"
                  label="Opening Deposit (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.annual_interest_rate"
                  label="Annual Rate (e.g. 0.025) *"
                  type="number"
                  step="0.0001"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model.number="form.daily_withdrawal_limit"
                  label="Daily Limit (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Create'" :loading="saving" unelevated />
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
  type_code: '',
  type_name: '',
  minimum_balance: 0,
  opening_deposit: 0,
  annual_interest_rate: 0,
  daily_withdrawal_limit: 0,
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'type_code', label: 'Code', field: 'type_code', sortable: true, align: 'left' },
  { name: 'type_name', label: 'Product Name', field: 'type_name', sortable: true, align: 'left' },
  { name: 'minimum_balance', label: 'Min Balance', field: 'minimum_balance', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'opening_deposit', label: 'Opening Deposit', field: 'opening_deposit', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'annual_interest_rate', label: 'Annual Rate', field: 'annual_interest_rate', format: val => `${(Number(val) * 100).toFixed(2)}%`, align: 'right' },
  { name: 'daily_withdrawal_limit', label: 'Daily Limit', field: 'daily_withdrawal_limit', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/account-types/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load account types' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    type_code: '',
    type_name: '',
    minimum_balance: 500,
    opening_deposit: 1000,
    annual_interest_rate: 0.025,
    daily_withdrawal_limit: 50000,
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    type_code: row.type_code,
    type_name: row.type_name,
    minimum_balance: Number(row.minimum_balance),
    opening_deposit: Number(row.opening_deposit),
    annual_interest_rate: Number(row.annual_interest_rate),
    daily_withdrawal_limit: Number(row.daily_withdrawal_limit),
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/account-types/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Account type updated' })
    } else {
      await api.post('/account-types/', form.value)
      $q.notify({ type: 'positive', message: 'Account type created' })
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
    message: `Delete account type "${row.type_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/account-types/${row.id}`)
      $q.notify({ type: 'positive', message: 'Account type deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(loadRows)
</script>
