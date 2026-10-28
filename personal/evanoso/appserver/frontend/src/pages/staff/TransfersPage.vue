<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Transfers</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered />

    <q-dialog v-model="showDialog">
      <q-card style="width: 440px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Transfer' : 'New Transfer' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-banner v-if="accountOptions.length < 2" dense class="bg-orange-1 text-dark">
            At least two accounts are needed. Create accounts under Staff &gt; Accounts first.
          </q-banner>
          <search-select
            v-model="form.source_account_id"
            label="Source Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="accountOptions.length < 2"
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
          <search-select
            v-model="form.destination_account_id"
            label="Destination Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="accountOptions.length < 2"
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
          <q-input v-model="form.transfer_reference" label="Transfer Reference" filled />
          <q-input v-model.number="form.amount" label="Amount" type="number" filled />
          <q-select v-model="form.transfer_type" label="Transfer type" filled emit-value map-options :options="transferTypeOptions" />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :disable="accountOptions.length < 2" @click="save" />
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
  { name: 'source_account_id', label: 'From account', field: row => optionLabel(accountOptions.value, row.source_account_id), align: 'left' },
  { name: 'destination_account_id', label: 'To account', field: row => optionLabel(accountOptions.value, row.destination_account_id), align: 'left' },
  { name: 'transfer_reference', label: 'Reference', field: 'transfer_reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
]

const rows = ref([])
const accountOptions = ref([])
const transferTypeOptions = [
  { label: 'Internal transfer', value: 'INTERNAL' },
  { label: 'Scheduled transfer', value: 'SCHEDULED' },
]
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: '',
  amount: 0,
  transfer_type: 'INTERNAL',
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/transfers/')
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
    destination_account_id: row.destination_account_id,
    transfer_reference: row.transfer_reference,
    amount: Number(row.amount),
    transfer_type: row.transfer_type,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/transfers/${editingId.value}`, form.value)
    } else {
      await api.post('/transfers/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Transfer saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete transfer "${row.transfer_reference}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Transfer deleted' })
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
