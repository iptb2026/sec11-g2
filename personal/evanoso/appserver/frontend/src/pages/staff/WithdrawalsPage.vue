<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Withdrawals</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered />

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Withdrawal' : 'New Withdrawal' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-banner v-if="accountOptions.length === 0" dense class="bg-orange-1 text-dark">
            No accounts are available. Create an account under Staff &gt; Accounts first.
          </q-banner>
          <search-select
            v-model="form.account_id"
            label="Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="accountOptions.length === 0"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.holder }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </search-select>
          <q-input
            v-if="form.account_id"
            :model-value="accountHolderName"
            label="Account Holder"
            filled
            readonly
          />
          <q-input v-model="form.reference_number" label="Reference Number" filled />
          <q-input v-model.number="form.amount" label="Amount" type="number" filled />
          <q-select
            v-model="form.withdrawal_channel"
            label="Channel"
            filled
            :options="channelOptions"
            :rules="[(val) => !!val || 'Channel is required']"
          />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :disable="accountOptions.length === 0" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: (row) => accountNumberByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'account_name', label: 'Account Name', field: (row) => accountHolderByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'withdrawal_channel', label: 'Channel', field: 'withdrawal_channel', align: 'left' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
]

const rows = ref([])
const accountOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({ account_id: null, reference_number: '', amount: 0, withdrawal_channel: '', remarks: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

const channelOptions = ['ATM', 'ONLINE', 'BRANCH', 'INTERBANK']

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/withdrawals/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }] = await Promise.all([
    api.get('/accounts/'),
    api.get('/users/'),
  ])

  const nameByUserId = {}
  users.forEach((u) => {
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`
  })

  accountOptions.value = accounts.map((a) => ({
    label: a.account_number,
    value: a.id,
    holder: nameByUserId[a.customer_id] || '',
  }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    withdrawal_channel: row.withdrawal_channel,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/withdrawals/${editingId.value}`, form.value)
    } else {
      await api.post('/withdrawals/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Withdrawal saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete withdrawal "${row.reference_number}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/withdrawals/${row.id}`)
      $q.notify({ type: 'positive', message: 'Withdrawal deleted' })
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
