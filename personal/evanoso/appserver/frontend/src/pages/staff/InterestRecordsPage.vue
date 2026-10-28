<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Interest Records</div>
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

    <!-- balance_before / balance_after are computed by the backend, not part of this form -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">New Interest Record</div>
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
          <search-select
            v-model="form.policy_id"
            label="Interest Policy"
            filled
            emit-value
            map-options
            :options="policyOptions"
          />
          <q-input v-model.number="form.amount_credited" label="Amount Credited" type="number" filled />
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
  { name: 'policy_id', label: 'Policy', field: row => optionLabel(policyOptions.value, row.policy_id), align: 'left' },
  { name: 'amount_credited', label: 'Amount Credited', field: 'amount_credited', align: 'right' },
  { name: 'balance_before', label: 'Balance Before', field: 'balance_before', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'credited_at', label: 'Credited At', field: 'credited_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const policyOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, policy_id: null, amount_credited: 0 })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/interest-records/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }, { data: policies }] = await Promise.all([api.get('/accounts/'), api.get('/users/'), api.get('/interest-policies/')])
  const names = Object.fromEntries(users.map(user => [user.id, `${user.first_name} ${user.last_name}`]))
  accountOptions.value = accounts.map(account => ({ label: account.account_number, holder: names[account.customer_id], value: account.id }))
  policyOptions.value = policies.map((p) => ({ label: p.policy_name, value: p.id }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/interest-records/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interest record created' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interest record #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interest record deleted' })
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
