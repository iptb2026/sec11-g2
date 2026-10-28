<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Interbank Transfers</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="check_circle" color="positive"
            title="Mark SUCCESS"
            @click="markStatus(props.row, 'SUCCESS')"
          />
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="cancel" color="negative"
            title="Mark FAILED"
            @click="markStatus(props.row, 'FAILED')"
          />
          <q-btn
            v-if="props.row.status === 'SUCCESS'"
            dense flat round icon="undo" color="warning"
            title="Reverse transfer"
            @click="markStatus(props.row, 'REVERSED')"
          />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 460px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Interbank Transfer' : 'New Interbank Transfer' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-banner v-if="accountOptions.length === 0 || bankOptions.length === 0" dense class="bg-orange-1 text-dark">
            <template v-if="accountOptions.length === 0">Create an account under Staff &gt; Accounts. </template>
            <template v-if="bankOptions.length === 0">Add a target bank under Admin &gt; Banks.</template>
          </q-banner>
          <search-select
            v-model="form.source_account_id"
            label="Source Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="accountOptions.length === 0"
          />
          <search-select
            v-model="form.target_bank_id"
            label="Target Bank"
            filled
            emit-value
            map-options
            :options="bankOptions"
            :disable="bankOptions.length === 0"
          />
          <q-input v-model="form.target_account_number" label="Target Account Number" filled />
          <q-input v-model="form.beneficiary_name" label="Beneficiary Name" filled />
          <q-input v-model="form.reference_number" label="Reference Number" filled />
          <q-input v-model.number="form.amount" label="Amount" type="number" filled />
          <q-input v-model.number="form.transfer_fee" label="Transfer Fee" type="number" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :disable="accountOptions.length === 0 || bankOptions.length === 0" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { optionLabel } from '@/utils/filter-options'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'source_account_id', label: 'Source account', field: row => optionLabel(accountOptions.value, row.source_account_id), align: 'left' },
  { name: 'target_bank_id', label: 'Target bank', field: row => optionLabel(bankOptions.value, row.target_bank_id), align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'transfer_fee', label: 'Fee', field: 'transfer_fee', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Settlement', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const bankOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  source_account_id: null,
  target_bank_id: null,
  target_account_number: '',
  beneficiary_name: '',
  reference_number: '',
  amount: 0,
  transfer_fee: 0,
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/interbank-transfers/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }, { data: banks }] = await Promise.all([api.get('/accounts/'), api.get('/users/'), api.get('/banks/')])
  const names = Object.fromEntries(users.map(user => [user.id, `${user.first_name} ${user.last_name}`]))
  accountOptions.value = accounts.map(account => ({ label: account.account_number, holder: names[account.customer_id], value: account.id }))
  bankOptions.value = banks.map((b) => ({ label: `${b.bank_code} - ${b.bank_name}`, value: b.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    source_account_id: row.source_account_id,
    target_bank_id: row.target_bank_id,
    target_account_number: row.target_account_number,
    beneficiary_name: row.beneficiary_name,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    transfer_fee: Number(row.transfer_fee),
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/interbank-transfers/${editingId.value}`, form.value)
    } else {
      await api.post('/interbank-transfers/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interbank transfer saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

async function markStatus (row, status) {
  try {
    await api.put(`/interbank-transfers/${row.id}/status`, { status })
    $q.notify({ type: 'positive', message: `Marked ${status}` })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Status update failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interbank transfer "${row.reference_number}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interbank-transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interbank transfer deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
