<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Assessed Fee Records</div>
        <div class="text-caption text-grey-7">Service charges, penalty assessments, and maintenance fee postings</div>
      </div>
      <q-btn color="negative" icon="receipt_long" label="Assess Fee" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No fee records assessed"
      >
        <template #body-cell-account_id="props">
          <q-td :props="props">
            <span class="text-weight-bold">{{ accountNumberById[props.row.account_id] || `Account #${props.row.account_id}` }}</span>
          </q-td>
        </template>
        <template #body-cell-fee_type_id="props">
          <q-td :props="props">
            <q-badge color="grey-8">{{ feeTypeNameById[props.row.fee_type_id] || `Fee Type #${props.row.fee_type_id}` }}</q-badge>
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
          <div class="text-h6">{{ editingId ? 'Edit Fee Assessment' : 'Assess Fee on Account' }}</div>
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
              :disable="!!editingId"
              :rules="[val => !!val || 'Account is required']"
            />
            <q-select
              v-model="form.fee_type_id"
              :options="feeTypeOptions"
              label="Fee Type *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Fee type is required']"
              @update:model-value="onFeeTypeSelected"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.amount_charged"
                  label="Amount Charged (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val > 0 || 'Amount must be > 0']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.assessed_date"
                  label="Assessed Date *"
                  filled
                  :rules="[val => !!val || 'Date is required']"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="negative" :label="editingId ? 'Update Record' : 'Post Fee Debit'" :loading="saving" unelevated />
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
const feeTypeOptions = ref([])
const rawFeeTypes = ref([])
const accountNumberById = ref({})
const feeTypeNameById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  account_id: null,
  fee_type_id: null,
  amount_charged: 50,
  assessed_date: new Date().toISOString().split('T')[0],
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'account_id', label: 'Account', field: 'account_id', align: 'left' },
  { name: 'fee_type_id', label: 'Fee Category', field: 'fee_type_id', align: 'left' },
  { name: 'amount_charged', label: 'Fee Charged', field: 'amount_charged', format: val => `-₱${Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`, align: 'right' },
  { name: 'assessed_date', label: 'Assessed Date', field: 'assessed_date', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

function onFeeTypeSelected (typeId) {
  const ft = rawFeeTypes.value.find(t => t.id === typeId)
  if (ft && ft.fixed_amount > 0) {
    form.value.amount_charged = Number(ft.fixed_amount)
  }
}

async function loadOptions () {
  try {
    const [accRes, feeRes] = await Promise.all([
      api.get('/accounts/'),
      api.get('/fee-types/'),
    ])
    accountOptions.value = accRes.data.map(a => ({ label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: a.id }))
    const accMap = {}
    accRes.data.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap

    rawFeeTypes.value = feeRes.data
    feeTypeOptions.value = feeRes.data.map(f => ({ label: `${f.fee_name} (₱${Number(f.fixed_amount).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`, value: f.id }))
    const fMap = {}
    feeRes.data.forEach(f => { fMap[f.id] = f.fee_name })
    feeTypeNameById.value = fMap
  } catch (err) {
    console.error('Failed to load options for fees', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/fee-records/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load fee records' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    account_id: accountOptions.value[0]?.value || null,
    fee_type_id: feeTypeOptions.value[0]?.value || null,
    amount_charged: 50,
    assessed_date: new Date().toISOString().split('T')[0],
  }
  if (feeTypeOptions.value[0]?.value) {
    onFeeTypeSelected(feeTypeOptions.value[0].value)
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    fee_type_id: row.fee_type_id,
    amount_charged: Number(row.amount_charged),
    assessed_date: row.assessed_date,
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/fee-records/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Fee record updated' })
    } else {
      await api.post('/fee-records/', form.value)
      $q.notify({ type: 'positive', message: 'Fee assessed and debited from account' })
    }
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

onMounted(async () => {
  await loadOptions()
  await loadRows()
})
</script>
