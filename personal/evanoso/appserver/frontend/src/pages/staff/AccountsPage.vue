<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Accounts</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-banner v-if="errorMessage" class="bank-feedback q-mb-md">{{ errorMessage }}<template #action><q-btn flat label="Retry" @click="loadPage" /></template></q-banner>
    <q-input v-model="accountSearch" filled dense clearable class="q-mb-md" label="Search accounts" placeholder="Account number, customer, status, or ID">
      <template #prepend><q-icon name="search" /></template>
    </q-input>
    <q-table
      :rows="groupedRows"
      :columns="columns"
      :row-key="rowKey"
      :loading="loading"
      flat
      bordered
      :pagination="{ rowsPerPage: 0 }"
      :rows-per-page-options="[0]"
    >
      <template v-slot:body="props">
        <q-tr v-if="props.row.isGroupHeader" :key="props.row.key">
          <q-td colspan="100%" class="account-group-row text-weight-bold">
            <q-icon name="person" class="q-mr-sm" />{{ props.row.groupLabel }}
          </q-td>
        </q-tr>
        <q-tr v-else :props="props">
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.name === 'actions'">
              <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
              <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
            </template>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 440px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Account' : 'New Account' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-banner v-if="accountTypeOptions.length === 0" dense class="bg-orange-1 text-dark">
            Create an account type in Admin &gt; Account Types before opening an account.
          </q-banner>
          <q-input v-model="form.account_number" label="Account Number" filled />
          <search-select
            v-model="form.customer_id"
            label="Customer"
            filled
            emit-value
            map-options
            :options="customerOptions"
          />
          <q-select
            v-model="form.account_type_id"
            label="Account Type"
            filled
            emit-value
            map-options
            :options="accountTypeOptions"
            :disable="accountTypeOptions.length === 0"
          />
          <q-input v-model="form.currency_code" label="Currency Code" filled />
          <q-input v-model="form.branch_code" label="Branch Code" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :disable="accountTypeOptions.length === 0" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { filterOptions, optionLabel } from '@/utils/filter-options'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account #', field: 'account_number', align: 'left' },
  { name: 'customer_id', label: 'Customer', field: row => customerNameById.value[row.customer_id] || `Customer #${row.customer_id}`, align: 'left' },
  { name: 'account_type_id', label: 'Account type', field: row => optionLabel(accountTypeOptions.value, row.account_type_id), align: 'left' },
  { name: 'available_balance', label: 'Available Balance', field: 'available_balance', format: money, align: 'right' },
  { name: 'ledger_balance', label: 'Ledger Balance', field: 'ledger_balance', format: money, align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const customerOptions = ref([])
const accountTypeOptions = ref([])
const customerNameById = ref({})
const loading = ref(false)
const errorMessage = ref('')
const accountSearch = ref('')
function money (value, row) {
  const currency = /^[A-Z]{3}$/.test(row.currency_code || '') ? row.currency_code : 'PHP'
  return Number.isFinite(Number(value)) ? new Intl.NumberFormat('en-PH', { style: 'currency', currency }).format(Number(value)) : '—'
}

function rowKey (row) {
  return row.isGroupHeader ? row.key : row.id
}

const matchingRows = computed(() => filterOptions(rows.value.map(row => ({
  label: `${row.id} ${row.account_number} ${customerNameById.value[row.customer_id] || ''} ${row.status}`,
  value: row,
})), accountSearch.value).map(option => option.value))

const groupedRows = computed(() => {
  const sorted = [...matchingRows.value].sort((a, b) => {
    const nameA = customerNameById.value[a.customer_id] || ''
    const nameB = customerNameById.value[b.customer_id] || ''
    return nameA.localeCompare(nameB) || String(a.account_number ?? '').localeCompare(String(b.account_number ?? ''))
  })

  const result = []
  let lastCustomerId = null
  for (const row of sorted) {
    if (row.customer_id !== lastCustomerId) {
      result.push({
        isGroupHeader: true,
        key: `group-${row.customer_id}`,
        groupLabel: customerNameById.value[row.customer_id] || `Customer #${row.customer_id}`,
      })
      lastCustomerId = row.customer_id
    }
    result.push(row)
  }
  return result
})
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_number: '',
  customer_id: null,
  account_type_id: null,
  currency_code: 'PHP',
  branch_code: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/accounts/')
    rows.value = data
  } catch {
    errorMessage.value = 'Accounts could not be loaded. Please try again.'
  } finally { loading.value = false }
}

async function loadOptions () {
  try {
  const { data: users } = await api.get('/users/')
  customerOptions.value = users.map((u) => ({ label: `${u.username} (${u.first_name} ${u.last_name})`, value: u.id }))
  customerNameById.value = Object.fromEntries(users.map((u) => [u.id, `${u.first_name} ${u.last_name}`]))

  const { data: types } = await api.get('/account-types/')
  accountTypeOptions.value = types.map((t) => ({ label: `${t.type_code} - ${t.type_name}`, value: t.id }))
  } catch {
    errorMessage.value = 'Customer and account details could not be loaded. Please try again.'
  }
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_number: row.account_number,
    customer_id: row.customer_id,
    account_type_id: row.account_type_id,
    currency_code: row.currency_code,
    branch_code: row.branch_code,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/accounts/${editingId.value}`, form.value)
    } else {
      await api.post('/accounts/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Account saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'The account could not be saved. Check the details and try again.' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete account "${row.account_number}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/accounts/${row.id}`)
      $q.notify({ type: 'positive', message: 'Account deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'This account could not be deleted. Accounts with linked activity must be retained.' })
    }
  })
}

async function loadPage () { errorMessage.value = ''; await Promise.all([loadRows(), loadOptions()]) }
onMounted(loadPage)
</script>
