<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Fee Records</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Fee Record' : 'New Fee Record' }}</div>
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
          <q-select
            v-model="form.fee_type_id"
            label="Fee Type"
            filled
            emit-value
            map-options
            :options="feeTypeOptions"
          />
          <q-input v-model="form.transaction_reference" label="Transaction Reference" filled />
          <q-input v-model.number="form.amount_charged" label="Amount Charged" type="number" filled />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" filled />
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
  { name: 'fee_type_id', label: 'Fee type', field: row => optionLabel(feeTypeOptions.value, row.fee_type_id), align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'amount_charged', label: 'Amount Charged', field: 'amount_charged', align: 'right' },
  { name: 'charged_at', label: 'Charged At', field: 'charged_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const feeTypeOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_id: null,
  fee_type_id: null,
  transaction_reference: '',
  amount_charged: 0,
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/fee-records/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }, { data: feeTypes }] = await Promise.all([api.get('/accounts/'), api.get('/users/'), api.get('/fee-types/')])
  const names = Object.fromEntries(users.map(user => [user.id, `${user.first_name} ${user.last_name}`]))
  accountOptions.value = accounts.map(account => ({ label: account.account_number, holder: names[account.customer_id], value: account.id }))
  feeTypeOptions.value = feeTypes.map((f) => ({ label: `${f.fee_code} - ${f.fee_name}`, value: f.id }))
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
    fee_type_id: row.fee_type_id,
    transaction_reference: row.transaction_reference,
    amount_charged: Number(row.amount_charged),
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/fee-records/${editingId.value}`, form.value)
    } else {
      await api.post('/fee-records/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Fee record saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete fee record #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/fee-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Fee record deleted' })
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
