<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Interest Credit Records</div>
        <div class="text-caption text-grey-7">Deposit interest computation, before/after balance snapshots, and postings</div>
      </div>
      <q-btn color="positive" icon="trending_up" label="Credit Interest" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No interest records found"
      >
        <template #body-cell-account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.account_id] || `Account #${props.row.account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-policy_id="props">
          <q-td :props="props">
            <q-badge color="purple-7">{{ policyNameById[props.row.policy_id] || `Policy #${props.row.policy_id}` }}</q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" align="center">
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Post Interest Credit</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_id"
              :options="accountOptions"
              label="Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Account is required']"
            />
            <q-select
              v-model="form.policy_id"
              :options="policyOptions"
              label="Applied Interest Policy *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Policy is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.amount_credited"
                  label="Amount Credited (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val > 0 || 'Must be > 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.calculation_date"
                  label="Calculation Date *"
                  filled
                  :rules="[val => !!val || 'Date is required']"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="positive" label="Credit Interest" :loading="saving" unelevated />
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
const policyOptions = ref([])
const accountNumberById = ref({})
const policyNameById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)

const form = ref({
  account_id: null,
  policy_id: null,
  amount_credited: 25,
  calculation_date: new Date().toISOString().split('T')[0],
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'account_id', label: 'Account', field: 'account_id', align: 'left' },
  { name: 'policy_id', label: 'Applied Policy', field: 'policy_id', align: 'left' },
  { name: 'balance_before', label: 'Balance Before', field: 'balance_before', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'amount_credited', label: 'Interest Credited', field: 'amount_credited', format: val => `+₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', format: val => `₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'calculation_date', label: 'Calc Date', field: 'calculation_date', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadOptions () {
  try {
    const [accRes, polRes] = await Promise.all([
      api.get('/accounts/'),
      api.get('/interest-policies/'),
    ])
    accountOptions.value = accRes.data.map(a => ({ label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: a.id }))
    const accMap = {}
    accRes.data.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap

    policyOptions.value = polRes.data.map(p => ({ label: `${p.policy_name} (${(Number(p.annual_rate) * 100).toFixed(2)}%)`, value: p.id }))
    const pMap = {}
    polRes.data.forEach(p => { pMap[p.id] = p.policy_name })
    policyNameById.value = pMap
  } catch (err) {
    console.error('Failed to load options for interest', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interest-records/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load interest records' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  form.value = {
    account_id: accountOptions.value[0]?.value || null,
    policy_id: policyOptions.value[0]?.value || null,
    amount_credited: 25,
    calculation_date: new Date().toISOString().split('T')[0],
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    await api.post('/interest-records/', form.value)
    $q.notify({ type: 'positive', message: 'Interest credited and balance updated' })
    showDialog.value = false
    await loadOptions()
    await loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interest credit record #${row.id}?`,
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

onMounted(async () => {
  await loadOptions()
  await loadRows()
})
</script>
