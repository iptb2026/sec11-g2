<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Interest Policies</div>
        <div class="text-caption text-grey-7">Configure deposit yield rates, compounding schedules, and terms</div>
      </div>
      <q-btn color="primary" icon="add" label="New Policy" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No interest policies configured"
      >
        <template #body-cell-account_type_id="props">
          <q-td :props="props">
            <q-badge color="purple-7">
              {{ accountTypeNameById[props.row.account_type_id] || `Type #${props.row.account_type_id}` }}
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
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Policy' : 'Create Policy' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.policy_name"
              label="Policy Name *"
              filled
              :rules="[val => !!val || 'Policy name is required']"
            />
            <q-select
              v-model="form.account_type_id"
              :options="accountTypeOptions"
              label="Applies To Account Type *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Account type is required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model.number="form.annual_rate"
                  label="Annual Rate (e.g. 0.025) *"
                  type="number"
                  step="0.0001"
                  filled
                  :rules="[val => val >= 0 || 'Must be >= 0']"
                />
              </div>
              <div class="col-6">
                <q-select
                  v-model="form.compounding_frequency"
                  :options="['DAILY', 'MONTHLY', 'QUARTERLY', 'YEARLY']"
                  label="Compounding *"
                  filled
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.effective_date"
                  label="Effective Date *"
                  filled
                  :rules="[val => !!val || 'Effective date is required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.expiration_date"
                  label="Expiration Date"
                  filled
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Create'" :loading="saving" unelevated />
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
const accountTypeOptions = ref([])
const accountTypeNameById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  account_type_id: null,
  policy_name: '',
  annual_rate: 0.025,
  compounding_frequency: 'MONTHLY',
  effective_date: new Date().toISOString().split('T')[0],
  expiration_date: null,
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'policy_name', label: 'Policy Name', field: 'policy_name', sortable: true, align: 'left' },
  { name: 'account_type_id', label: 'Account Type', field: 'account_type_id', align: 'center' },
  { name: 'annual_rate', label: 'Annual Rate', field: 'annual_rate', format: val => `${(Number(val) * 100).toFixed(2)}%`, align: 'right' },
  { name: 'compounding_frequency', label: 'Compounding', field: 'compounding_frequency', align: 'center' },
  { name: 'effective_date', label: 'Effective Date', field: 'effective_date', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadOptions () {
  try {
    const { data: actypes } = await api.get('/account-types/')
    accountTypeOptions.value = actypes.map(a => ({ label: `${a.type_name} (${a.type_code})`, value: a.id }))
    const actMap = {}
    actypes.forEach(a => { actMap[a.id] = a.type_name })
    accountTypeNameById.value = actMap
  } catch (err) {
    console.error('Failed to load account types for policies', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interest-policies/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load policies' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    account_type_id: accountTypeOptions.value[0]?.value || null,
    policy_name: '',
    annual_rate: 0.025,
    compounding_frequency: 'MONTHLY',
    effective_date: new Date().toISOString().split('T')[0],
    expiration_date: null,
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_type_id: row.account_type_id,
    policy_name: row.policy_name,
    annual_rate: Number(row.annual_rate),
    compounding_frequency: row.compounding_frequency,
    effective_date: row.effective_date,
    expiration_date: row.expiration_date || null,
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/interest-policies/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Policy updated' })
    } else {
      await api.post('/interest-policies/', form.value)
      $q.notify({ type: 'positive', message: 'Policy created' })
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
    message: `Delete interest policy "${row.policy_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-policies/${row.id}`)
      $q.notify({ type: 'positive', message: 'Policy deleted' })
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
