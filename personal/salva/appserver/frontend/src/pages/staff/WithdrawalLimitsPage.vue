<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Daily Withdrawal Limits</div>
        <div class="text-caption text-grey-7">Account-level daily withdrawal controls and usage tracking</div>
      </div>
      <q-btn color="primary" icon="add" label="Set New Limit" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No withdrawal limits configured"
      >
        <template #body-cell-account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.account_id] || `Account #${props.row.account_id}` }}</span>
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
      <q-card style="min-width: 420px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Update Limit' : 'Configure Limit' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-select
              v-if="!editingId"
              v-model="form.account_id"
              :options="accountOptions"
              label="Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Account is required']"
            />
            <q-input
              v-model.number="form.daily_limit_amount"
              label="Daily Limit Amount (₱) *"
              type="number"
              step="0.01"
              filled
              :rules="[val => val > 0 || 'Must be > 0']"
            />
            <q-input
              v-model="form.last_reset_date"
              label="Last Reset Date (YYYY-MM-DD) *"
              filled
              :rules="[val => !!val || 'Reset date is required']"
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Save'" :loading="saving" unelevated />
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
const editingId = ref(null)

const form = ref({
  account_id: null,
  daily_limit_amount: 50000,
  daily_used_amount: 0,
  last_reset_date: new Date().toISOString().split('T')[0],
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'account_id', label: 'Account', field: 'account_id', align: 'left' },
  { name: 'daily_limit_amount', label: 'Daily Limit', field: 'daily_limit_amount', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'daily_used_amount', label: 'Used Today', field: 'daily_used_amount', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'last_reset_date', label: 'Last Reset', field: 'last_reset_date', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadOptions () {
  try {
    const { data: accounts } = await api.get('/accounts/')
    accountOptions.value = accounts.map(a => ({ label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: a.id }))
    const accMap = {}
    accounts.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap
  } catch (err) {
    console.error('Failed to load accounts for limits', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/withdrawal-limits/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load limits' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    account_id: accountOptions.value[0]?.value || null,
    daily_limit_amount: 50000,
    daily_used_amount: 0,
    last_reset_date: new Date().toISOString().split('T')[0],
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    daily_limit_amount: Number(row.daily_limit_amount),
    daily_used_amount: Number(row.daily_used_amount),
    last_reset_date: row.last_reset_date,
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      // WithdrawalLimitUpdate schema accepts daily_limit_amount and last_reset_date
      await api.put(`/withdrawal-limits/${editingId.value}`, {
        daily_limit_amount: form.value.daily_limit_amount,
        last_reset_date: form.value.last_reset_date,
      })
      $q.notify({ type: 'positive', message: 'Limit updated' })
    } else {
      await api.post('/withdrawal-limits/', form.value)
      $q.notify({ type: 'positive', message: 'Limit configured' })
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
    message: `Remove withdrawal limit for ${accountNumberById.value[row.account_id] || 'this account'}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/withdrawal-limits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Limit removed' })
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
