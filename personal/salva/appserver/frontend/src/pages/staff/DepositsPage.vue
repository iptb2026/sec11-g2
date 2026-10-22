<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Cash & Check Deposits</div>
        <div class="text-caption text-grey-7">Process account credit deposits with row-level transaction safety</div>
      </div>
      <q-btn color="positive" icon="savings" label="Process Deposit" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No deposit records found"
      >
        <template #body-cell-account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.account_id] || `Account #${props.row.account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-deposit_channel="props">
          <q-td :props="props" align="center">
            <q-badge color="teal">{{ props.row.deposit_channel }}</q-badge>
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
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Deposit Record' : 'Record Deposit' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.reference_number"
              label="Reference Number *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Reference number is required']"
            />
            <q-select
              v-model="form.account_id"
              :options="accountOptions"
              label="Target Account *"
              filled
              emit-value
              map-options
              :disable="!!editingId"
              :rules="[val => !!val || 'Account is required']"
            />
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
                  v-model="form.deposit_channel"
                  :options="['CASH', 'ATM', 'ONLINE', 'INTERBANK']"
                  label="Channel *"
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
            <q-btn type="submit" color="positive" :label="editingId ? 'Update Record' : 'Submit Deposit'" :loading="saving" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'

const $q = useQuasar()
const authStore = useAuthStore()
const rows = ref([])
const accountOptions = ref([])
const accountNumberById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  account_id: null,
  reference_number: '',
  amount: 1000,
  deposit_channel: 'CASH',
  deposited_by_user_id: null,
  remarks: '',
  transaction_date: new Date().toISOString(),
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'reference_number', label: 'Reference #', field: 'reference_number', sortable: true, align: 'left' },
  { name: 'account_id', label: 'Account', field: 'account_id', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', format: val => `+₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel', align: 'center' },
  { name: 'remarks', label: 'Remarks', field: 'remarks', align: 'left' },
  { name: 'created_at', label: 'Posted At', field: 'created_at', format: val => val ? new Date(val).toLocaleString() : '', align: 'left' },
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
    console.error('Failed to load accounts for deposits', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/deposits/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load deposits' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  const randomRef = `DEP-${Date.now().toString().slice(-6)}`
  form.value = {
    account_id: accountOptions.value[0]?.value || null,
    reference_number: randomRef,
    amount: 1000,
    deposit_channel: 'CASH',
    deposited_by_user_id: authStore.userId,
    remarks: 'Cash counter deposit',
    transaction_date: new Date().toISOString(),
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    deposit_channel: row.deposit_channel,
    deposited_by_user_id: row.deposited_by_user_id,
    remarks: row.remarks || '',
    transaction_date: row.transaction_date,
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/deposits/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Deposit record updated' })
    } else {
      await api.post('/deposits/', form.value)
      $q.notify({ type: 'positive', message: 'Deposit processed and balance credited' })
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
    message: `Delete deposit record ${row.reference_number}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/deposits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Deposit record deleted' })
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
