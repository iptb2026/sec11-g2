<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Ledger Entries</div>
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

    <!-- balance_after is a point-in-time snapshot the backend fills in automatically -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">New Ledger Entry</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <search-select
            v-model="form.account_id"
            label="Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
          />
          <q-input v-model="form.transaction_reference" label="Transaction Reference" filled />
          <q-select v-model="form.transaction_type" label="Transaction type" filled emit-value map-options :options="transactionTypeOptions" />
          <q-input v-model.number="form.debit_amount" label="Debit Amount" type="number" filled />
          <q-input v-model.number="form.credit_amount" label="Credit Amount" type="number" filled />
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
import { optionLabel } from '@/utils/filter-options'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account', field: row => optionLabel(accountOptions.value, row.account_id), align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'debit_amount', label: 'Debit', field: 'debit_amount', align: 'right' },
  { name: 'credit_amount', label: 'Credit', field: 'credit_amount', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const transactionTypeOptions = [
  { label: 'Deposit', value: 'DEPOSIT' },
  { label: 'Withdrawal', value: 'WITHDRAWAL' },
  { label: 'Transfer debit', value: 'TRANSFER_DEBIT' },
  { label: 'Transfer credit', value: 'TRANSFER_CREDIT' },
  { label: 'Fee', value: 'FEE' },
  { label: 'Interest', value: 'INTEREST' },
  { label: 'Interbank debit', value: 'INTERBANK_DEBIT' },
  { label: 'Interbank credit', value: 'INTERBANK_CREDIT' },
  { label: 'Reversal', value: 'REVERSAL' },
]
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, transaction_reference: '', transaction_type: '', debit_amount: 0, credit_amount: 0 })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/ledger-entries/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }] = await Promise.all([api.get('/accounts/'), api.get('/users/')])
  const names = Object.fromEntries(users.map(user => [user.id, `${user.first_name} ${user.last_name}`]))
  accountOptions.value = accounts.map(account => ({ label: account.account_number, holder: names[account.customer_id], value: account.id }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/ledger-entries/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Ledger entry created' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
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

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
