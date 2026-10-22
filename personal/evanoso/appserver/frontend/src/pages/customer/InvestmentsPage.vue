<template>
  <q-page class="customer-flow-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow">Customer banking</div>
        <h1 class="page-title">Investments</h1>
        <p class="page-subtitle">Allocate and track funds from your bank account.</p>
      </div>
    </div>

    <q-banner dense class="customer-disclosure q-mb-md">
      Allocations are tracked locally with no market returns or external investment provider connected. You can redeem the principal at any time.
    </q-banner>
    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">{{ errorMessage }}</q-banner>

    <div class="customer-workspace-grid">
      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="trending_up" size="19px" /></div>
          <div>
            <h2 class="section-heading">Create allocation</h2>
            <p class="customer-panel-subtitle">Choose a tracking term and set aside principal.</p>
          </div>
        </div>

        <q-form class="customer-form" @submit.prevent="allocateFunds">
          <q-select v-model="form.account_id" label="Allocate from account" filled emit-value map-options :options="accountOptions" :disable="loading || accountOptions.length === 0" :rules="[(value) => value !== null || 'Choose an account']" />
          <q-select v-model="form.plan_code" label="Tracking term" filled emit-value map-options :options="planOptions" :rules="[(value) => !!value || 'Choose a term']" />
          <q-input v-model.number="form.amount" label="Amount (PHP)" type="number" min="0.01" step="0.01" filled :rules="[(value) => Number(value) > 0 || 'Enter an amount greater than zero']" />
          <q-banner v-if="accountOptions.length === 0 && !loading" dense class="bg-orange-1 text-dark">
            No active account is available for an allocation.
          </q-banner>
          <div class="customer-form-actions">
            <q-btn type="submit" color="primary" unelevated no-caps icon="trending_up" label="Allocate funds" :loading="submitting" :disable="loading || accountOptions.length === 0" />
          </div>
        </q-form>
      </section>

      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="savings" size="19px" /></div>
          <div>
            <h2 class="section-heading">Your allocations</h2>
            <p class="customer-panel-subtitle">Active principal remains part of your account ledger balance.</p>
          </div>
        </div>
        <q-table :rows="investments" :columns="columns" row-key="id" :loading="loading" flat :pagination="{ rowsPerPage: 6, sortBy: 'created_at', descending: true }" no-data-label="No investment allocations yet">
          <template #body-cell-amount="props"><q-td :props="props" class="text-weight-bold">PHP {{ format(props.row.amount) }}</q-td></template>
          <template #body-cell-status="props"><q-td :props="props"><q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : 'grey'">{{ props.row.status }}</q-badge></q-td></template>
          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn v-if="props.row.status === 'ACTIVE'" flat dense no-caps label="Redeem" :loading="redeemingId === props.row.id" @click="redeem(props.row)" />
            </q-td>
          </template>
        </q-table>
      </section>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const accounts = ref([])
const investments = ref([])
const loading = ref(true)
const submitting = ref(false)
const redeemingId = ref(null)
const errorMessage = ref('')
const form = ref({ account_id: null, plan_code: 'SHORT_TERM', amount: null })
const planOptions = [
  { label: 'Short term · 3 months', value: 'SHORT_TERM' },
  { label: 'Medium term · 6 months', value: 'MEDIUM_TERM' },
  { label: 'Long term · 12 months', value: 'LONG_TERM' },
]
const accountOptions = computed(() => accounts.value
  .filter((account) => account.status === 'ACTIVE')
  .map((account) => ({ label: `${account.account_number} · PHP ${format(account.available_balance)}`, value: account.id })))
const columns = [
  { name: 'created_at', label: 'Started', field: 'created_at', align: 'left', sortable: true },
  { name: 'plan_code', label: 'Term', field: (row) => `${row.term_months} months`, align: 'left' },
  { name: 'amount', label: 'Principal', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: '', field: 'actions', align: 'right' },
]

function format (value) {
  return Number(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData () {
  loading.value = true
  errorMessage.value = ''
  try {
    const [accountResponse, investmentResponse] = await Promise.all([
      api.get('/customer/accounts/'),
      api.get('/customer/investments/'),
    ])
    accounts.value = accountResponse.data
    investments.value = investmentResponse.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load investment data.'
  } finally {
    loading.value = false
  }
}

async function allocateFunds () {
  if (submitting.value) return
  submitting.value = true
  try {
    await api.post('/customer/investments/', form.value)
    form.value = { account_id: null, plan_code: 'SHORT_TERM', amount: null }
    $q.notify({ type: 'positive', message: 'Investment allocation recorded' })
    await loadData()
  } catch (error) {
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Allocation could not be recorded.' })
  } finally {
    submitting.value = false
  }
}

function redeem (investment) {
  $q.dialog({
    title: 'Redeem principal',
    message: `Return PHP ${format(investment.amount)} to your available account balance? No returns are calculated.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    redeemingId.value = investment.id
    try {
      await api.post(`/customer/investments/${investment.id}/redeem`)
      $q.notify({ type: 'positive', message: 'Principal returned to your account' })
      await loadData()
    } catch (error) {
      $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Redemption could not be recorded.' })
    } finally {
      redeemingId.value = null
    }
  })
}

onMounted(loadData)
</script>
