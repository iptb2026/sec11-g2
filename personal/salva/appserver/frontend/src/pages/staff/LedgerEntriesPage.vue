<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">General Ledger Journal</div>
        <div class="text-caption text-grey-7">Official double-entry accounting ledger and balance audit trails</div>
      </div>
      <q-btn color="primary" icon="menu_book" label="Post Ledger Entry" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No ledger entries found"
      >
        <template #body-cell-account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.account_id] || `Account #${props.row.account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-transaction_type="props">
          <q-td :props="props" align="center">
            <q-badge color="blue-grey-8">{{ props.row.transaction_type }}</q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" align="center">
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Post Ledger Journal Entry</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_id"
              :options="accountOptions"
              label="Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Account is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.debit_amount"
                  label="Debit Amount (₱)"
                  type="number"
                  step="0.01"
                  filled
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model.number="form.credit_amount"
                  label="Credit Amount (₱)"
                  type="number"
                  step="0.01"
                  filled
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.transaction_type"
                  label="Transaction Type *"
                  filled
                  :rules="[val => !!val || 'Type is required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.reference_number"
                  label="Reference #"
                  filled
                />
              </div>
            </div>
            <q-input
              v-model="form.description"
              label="Description / Memo"
              filled
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" label="Post Entry" :loading="saving" unelevated />
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

const form = ref({
  account_id: null,
  debit_amount: 0,
  credit_amount: 0,
  transaction_type: 'MANUAL_ADJUSTMENT',
  reference_number: '',
  description: '',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'account_id', label: 'Account', field: 'account_id', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'center' },
  { name: 'debit_amount', label: 'Debit (DR)', field: 'debit_amount', format: val => val > 0 ? `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}` : '-', align: 'right' },
  { name: 'credit_amount', label: 'Credit (CR)', field: 'credit_amount', format: val => val > 0 ? `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}` : '-', align: 'right' },
  { name: 'balance_after', label: 'Balance Snapshot', field: 'balance_after', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'reference_number', label: 'Reference #', field: 'reference_number', align: 'left' },
  { name: 'entry_date', label: 'Posted At', field: 'entry_date', format: val => val ? new Date(val).toLocaleString() : '', align: 'left' },
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
    console.error('Failed to load accounts for ledger', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/ledger-entries/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load ledger entries' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  const randomRef = `LDG-${Date.now().toString().slice(-6)}`
  form.value = {
    account_id: accountOptions.value[0]?.value || null,
    debit_amount: 0,
    credit_amount: 100,
    transaction_type: 'MANUAL_CREDIT',
    reference_number: randomRef,
    description: 'Manual ledger posting',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    await api.post('/ledger-entries/', form.value)
    $q.notify({ type: 'positive', message: 'Ledger journal entry posted' })
    showDialog.value = false
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
    message: `Delete ledger entry #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/ledger-entries/${row.id}`)
      $q.notify({ type: 'positive', message: 'Ledger entry deleted' })
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
