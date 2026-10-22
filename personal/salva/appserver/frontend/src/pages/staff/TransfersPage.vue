<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Internal Account Transfers</div>
        <div class="text-caption text-grey-7">Real-time book transfer between Salva accounts with atomic dual debit/credit</div>
      </div>
      <q-btn color="primary" icon="swap_horiz" label="New Transfer" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No transfer records found"
      >
        <template #body-cell-source_account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.source_account_id] || `Account #${props.row.source_account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-destination_account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.destination_account_id] || `Account #${props.row.destination_account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-status="props">
          <q-td :props="props" align="center">
            <q-badge :color="props.row.status === 'SUCCESS' ? 'positive' : 'warning'">{{ props.row.status }}</q-badge>
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
      <q-card style="min-width: 480px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Transfer Record' : 'Execute Internal Transfer' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.transfer_reference"
              label="Transfer Reference *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Reference is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-select
                  v-model="form.source_account_id"
                  :options="accountOptions"
                  label="From Account *"
                  filled
                  emit-value
                  map-options
                  :disable="!!editingId"
                  :rules="[val => !!val || 'Source required']"
                />
              </div>
              <div class="col-6">
                <q-select
                  v-model="form.destination_account_id"
                  :options="accountOptions"
                  label="To Account *"
                  filled
                  emit-value
                  map-options
                  :disable="!!editingId"
                  :rules="[val => !!val || 'Destination required', val => val !== form.source_account_id || 'Must be different']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.amount"
                  label="Amount (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :disable="!!editingId"
                  :rules="[val => val > 0 || 'Amount must be > 0']"
                />
              </div>
              <div class="col-6">
                <q-select
                  v-model="form.transfer_type"
                  :options="['INTERNAL', 'SCHEDULED']"
                  label="Type *"
                  filled
                  :disable="!!editingId"
                />
              </div>
            </div>
            <q-input
              v-model="form.remarks"
              label="Remarks / Memo"
              filled
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update Record' : 'Confirm Transfer'" :loading="saving" unelevated />
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
const accountOptions = ref([])
const accountNumberById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: '',
  amount: 500,
  transfer_type: 'INTERNAL',
  remarks: '',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'transfer_reference', label: 'Reference #', field: 'transfer_reference', sortable: true, align: 'left' },
  { name: 'source_account_id', label: 'From Account', field: 'source_account_id', align: 'left' },
  { name: 'destination_account_id', label: 'To Account', field: 'destination_account_id', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'remarks', label: 'Remarks', field: 'remarks', align: 'left' },
  { name: 'created_at', label: 'Timestamp', field: 'created_at', format: val => val ? new Date(val).toLocaleString() : '', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadAccounts () {
  try {
    const { data: accounts } = await api.get('/accounts/')
    accountOptions.value = accounts.map(a => ({ label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: a.id }))
    const accMap = {}
    accounts.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap
  } catch (err) {
    console.error('Failed to load accounts for transfers', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/transfers/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load transfers' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  const randomRef = `TRF-${Date.now().toString().slice(-6)}`
  form.value = {
    source_account_id: accountOptions.value[0]?.value || null,
    destination_account_id: accountOptions.value[1]?.value || null,
    transfer_reference: randomRef,
    amount: 500,
    transfer_type: 'INTERNAL',
    remarks: 'Internal transfer',
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    source_account_id: row.source_account_id,
    destination_account_id: row.destination_account_id,
    transfer_reference: row.transfer_reference,
    amount: Number(row.amount),
    transfer_type: row.transfer_type,
    remarks: row.remarks || '',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/transfers/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Transfer record updated' })
    } else {
      await api.post('/transfers/', form.value)
      $q.notify({ type: 'positive', message: 'Transfer executed successfully' })
    }
    showDialog.value = false
    await loadAccounts()
    await loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete transfer record ${row.transfer_reference}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Transfer record deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(async () => {
  await loadAccounts()
  await loadRows()
})
</script>
