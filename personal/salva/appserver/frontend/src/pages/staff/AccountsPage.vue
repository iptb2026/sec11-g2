<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Bank Accounts</div>
        <div class="text-caption text-grey-7">Account management, status controls, and balance monitoring</div>
      </div>
      <q-btn color="primary" icon="add" label="Open Account" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No accounts found"
      >
        <template #body-cell-customer_id="props">
          <q-td :props="props">
            <span class="text-weight-medium">{{ customerNameById[props.row.customer_id] || `Customer #${props.row.customer_id}` }}</span>
          </q-td>
        </template>

        <template #body-cell-account_type_id="props">
          <q-td :props="props">
            <q-badge color="blue-8">
              {{ accountTypeNameById[props.row.account_type_id] || `Type #${props.row.account_type_id}` }}
            </q-badge>
          </q-td>
        </template>

        <template #body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : (props.row.status === 'FROZEN' ? 'warning' : 'negative')">
              {{ props.row.status }}
            </q-badge>
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
          <div class="text-h6">{{ editingId ? 'Update Account Status' : 'Open New Account' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.account_number"
              label="Account Number *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Account number is required']"
            />
            <q-select
              v-model="form.customer_id"
              :options="customerOptions"
              label="Account Owner (Customer) *"
              filled
              emit-value
              map-options
              :disable="!!editingId"
              :rules="[val => !!val || 'Customer is required']"
            />
            <q-select
              v-model="form.account_type_id"
              :options="accountTypeOptions"
              label="Account Product Type *"
              filled
              emit-value
              map-options
              :disable="!!editingId"
              :rules="[val => !!val || 'Account type is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.currency_code"
                  label="Currency"
                  filled
                  :disable="!!editingId"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.branch_code"
                  label="Branch Code"
                  filled
                  :disable="!!editingId"
                />
              </div>
            </div>
            <q-select
              v-if="editingId"
              v-model="form.status"
              :options="['ACTIVE', 'FROZEN', 'CLOSED']"
              label="Account Status *"
              filled
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Open Account'" :loading="saving" unelevated />
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
const customerOptions = ref([])
const accountTypeOptions = ref([])
const customerNameById = ref({})
const accountTypeNameById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  account_number: '',
  customer_id: null,
  account_type_id: null,
  currency_code: 'PHP',
  branch_code: 'BR-MAIN-01',
  status: 'ACTIVE',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'account_number', label: 'Account #', field: 'account_number', sortable: true, align: 'left' },
  { name: 'customer_id', label: 'Customer', field: 'customer_id', align: 'left' },
  { name: 'account_type_id', label: 'Account Type', field: 'account_type_id', align: 'center' },
  { name: 'available_balance', label: 'Available Balance', field: 'available_balance', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'ledger_balance', label: 'Ledger Balance', field: 'ledger_balance', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadOptions () {
  try {
    const [usersRes, actypesRes] = await Promise.all([
      api.get('/users/'),
      api.get('/account-types/'),
    ])
    customerOptions.value = usersRes.data.map(u => ({ label: `${u.first_name} ${u.last_name} (${u.username})`, value: u.id }))
    const custMap = {}
    usersRes.data.forEach(u => { custMap[u.id] = `${u.first_name} ${u.last_name}` })
    customerNameById.value = custMap

    accountTypeOptions.value = actypesRes.data.map(a => ({ label: `${a.type_name} (${a.type_code})`, value: a.id }))
    const actMap = {}
    actypesRes.data.forEach(a => { actMap[a.id] = a.type_name })
    accountTypeNameById.value = actMap
  } catch (err) {
    console.error('Failed to load options', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/accounts/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load accounts' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  const randomSuffix = Math.floor(1000 + Math.random() * 9000)
  form.value = {
    account_number: `SA-2026-${randomSuffix}`,
    customer_id: customerOptions.value[0]?.value || null,
    account_type_id: accountTypeOptions.value[0]?.value || null,
    currency_code: 'PHP',
    branch_code: 'BR-MAIN-01',
    status: 'ACTIVE',
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_number: row.account_number,
    customer_id: row.customer_id,
    account_type_id: row.account_type_id,
    currency_code: row.currency_code || 'PHP',
    branch_code: row.branch_code || 'BR-MAIN-01',
    status: row.status || 'ACTIVE',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/accounts/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Account updated successfully' })
    } else {
      await api.post('/accounts/', form.value)
      $q.notify({ type: 'positive', message: 'Account opened successfully' })
    }
    showDialog.value = false
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete account ${row.account_number}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/accounts/${row.id}`)
      $q.notify({ type: 'positive', message: 'Account deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(async () => {
  await loadOptions()
  await loadRows()
})
</script>
