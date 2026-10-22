<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Interbank Transfers</div>
        <div class="text-caption text-grey-7">InstaPay and PESONet outward clearing and settlement monitoring</div>
      </div>
      <q-btn color="primary" icon="send" label="Initiate Outward Transfer" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No interbank transfers found"
      >
        <template #body-cell-source_account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.source_account_id] || `Account #${props.row.source_account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-target_bank_id="props">
          <q-td :props="props">
            <q-badge color="indigo">{{ bankNameById[props.row.target_bank_id] || `Bank #${props.row.target_bank_id}` }}</q-badge>
          </q-td>
        </template>
        <template #body-cell-status="props">
          <q-td :props="props" align="center">
            <q-badge :color="props.row.status === 'SUCCESS' ? 'positive' : (props.row.status === 'PROCESSING' ? 'primary' : 'negative')">
              {{ props.row.status }}
            </q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" class="q-gutter-xs">
            <q-btn flat round dense icon="sync_alt" color="primary" @click="openStatusUpdate(props.row)">
              <q-tooltip>Update Clearing Status</q-tooltip>
            </q-btn>
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <!-- Create Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 480px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Initiate Outward Interbank Transfer</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.reference_number"
              label="Reference Number *"
              filled
              :rules="[val => !!val || 'Reference is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-select
                  v-model="form.source_account_id"
                  :options="accountOptions"
                  label="Source Account *"
                  filled
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Source required']"
                />
              </div>
              <div class="col-6">
                <q-select
                  v-model="form.target_bank_id"
                  :options="bankOptions"
                  label="Receiving Bank *"
                  filled
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Target bank required']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.target_account_number"
                  label="Target Account # *"
                  filled
                  :rules="[val => !!val || 'Target account required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.beneficiary_name"
                  label="Beneficiary Name"
                  filled
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.amount"
                  label="Amount (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val > 0 || 'Amount must be > 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model.number="form.transfer_fee"
                  label="Transfer Fee (₱)"
                  type="number"
                  step="0.01"
                  filled
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" label="Send Transfer" :loading="saving" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Status Update Dialog -->
    <q-dialog v-model="showStatusDialog" persistent>
      <q-card style="min-width: 380px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Settlement Status</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <div class="text-subtitle2">Reference: {{ selectedRow?.reference_number }}</div>
          <q-select
            v-model="newStatus"
            :options="['PROCESSING', 'SUCCESS', 'FAILED', 'REVERSED']"
            label="Clearing Status *"
            filled
          />
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Update Status" :loading="saving" @click="saveStatus" unelevated />
        </q-card-actions>
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
const bankOptions = ref([])
const accountNumberById = ref({})
const bankNameById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const showStatusDialog = ref(false)
const selectedRow = ref(null)
const newStatus = ref('SUCCESS')

const form = ref({
  source_account_id: null,
  target_bank_id: null,
  target_account_number: '',
  beneficiary_name: '',
  reference_number: '',
  amount: 1000,
  transfer_fee: 25,
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'reference_number', label: 'Reference #', field: 'reference_number', sortable: true, align: 'left' },
  { name: 'source_account_id', label: 'Source Account', field: 'source_account_id', align: 'left' },
  { name: 'target_bank_id', label: 'Target Bank', field: 'target_bank_id', align: 'left' },
  { name: 'target_account_number', label: 'Target Account #', field: 'target_account_number', align: 'left' },
  { name: 'beneficiary_name', label: 'Beneficiary', field: 'beneficiary_name', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'transfer_fee', label: 'Fee', field: 'transfer_fee', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadOptions () {
  try {
    const [accRes, bankRes] = await Promise.all([
      api.get('/accounts/'),
      api.get('/banks/'),
    ])
    accountOptions.value = accRes.data.map(a => ({ label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: a.id }))
    const accMap = {}
    accRes.data.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap

    bankOptions.value = bankRes.data.map(b => ({ label: `${b.bank_name} (${b.bank_code})`, value: b.id }))
    const bMap = {}
    bankRes.data.forEach(b => { bMap[b.id] = b.bank_code })
    bankNameById.value = bMap
  } catch (err) {
    console.error('Failed to load options for interbank', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interbank-transfers/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load interbank transfers' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  const randomRef = `IBT-${Date.now().toString().slice(-6)}`
  form.value = {
    source_account_id: accountOptions.value[0]?.value || null,
    target_bank_id: bankOptions.value[0]?.value || null,
    target_account_number: '1234567890',
    beneficiary_name: 'External Payee',
    reference_number: randomRef,
    amount: 1000,
    transfer_fee: 25,
  }
  showDialog.value = true
}

function openStatusUpdate (row) {
  selectedRow.value = row
  newStatus.value = row.status
  showStatusDialog.value = true
}

async function save () {
  saving.value = true
  try {
    await api.post('/interbank-transfers/', form.value)
    $q.notify({ type: 'positive', message: 'Interbank transfer initiated' })
    showDialog.value = false
    await loadOptions()
    await loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

async function saveStatus () {
  if (!selectedRow.value) return
  saving.value = true
  try {
    await api.put(`/interbank-transfers/${selectedRow.value.id}/status`, { status: newStatus.value })
    $q.notify({ type: 'positive', message: 'Status updated successfully' })
    showStatusDialog.value = false
    await loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Update failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interbank transfer record ${row.reference_number}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interbank-transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Record deleted' })
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
