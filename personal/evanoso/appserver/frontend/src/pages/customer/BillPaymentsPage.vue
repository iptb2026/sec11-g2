<template>
  <q-page class="customer-flow-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow">Customer banking</div>
        <h1 class="page-title">Pay bills</h1>
        <p class="page-subtitle">Record a bill payment from one of your accounts.</p>
      </div>
    </div>

    <q-banner dense class="customer-disclosure q-mb-md">
      Payments are recorded in this banking workspace; external biller settlement is not connected.
    </q-banner>
    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">{{ errorMessage }}</q-banner>

    <div class="customer-workspace-grid">
      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="receipt_long" size="19px" /></div>
          <div>
            <h2 class="section-heading">Payment details</h2>
            <p class="customer-panel-subtitle">A receipt reference is generated after submission.</p>
          </div>
        </div>

        <q-form class="customer-form" @submit.prevent="reviewOpen = true">
          <search-select
            v-model="form.account_id"
            label="Pay from account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="loading || accountOptions.length === 0"
            :rules="[(value) => value !== null || 'Choose an account']"
          />
          <q-input v-model.trim="form.biller_name" label="Biller" maxlength="100" filled :rules="[(value) => !!value || 'Biller is required']" />
          <q-input v-model.trim="form.biller_reference" label="Customer or invoice reference" maxlength="100" filled :rules="[(value) => !!value || 'Reference is required']" />
          <q-input v-model.number="form.amount" label="Amount (PHP)" type="number" min="0.01" step="0.01" filled :rules="[(value) => Number(value) > 0 || 'Enter an amount greater than zero']" />
          <q-banner v-if="accountOptions.length === 0 && !loading" dense class="bg-orange-1 text-dark">
            No active account is available for payments.
          </q-banner>
          <div class="customer-form-actions">
            <q-btn type="submit" color="primary" unelevated no-caps icon="receipt_long" label="Review payment" :loading="submitting" :disable="loading || accountOptions.length === 0" />
          </div>
        </q-form>
      </section>

      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="history" size="19px" /></div>
          <div>
            <h2 class="section-heading">Payment history</h2>
            <p class="customer-panel-subtitle">Your recorded bill payments.</p>
          </div>
        </div>
        <q-table :rows="payments" :columns="columns" row-key="id" :loading="loading" flat :pagination="{ rowsPerPage: 6, sortBy: 'created_at', descending: true }" no-data-label="No bill payments yet">
          <template #body-cell-amount="props"><q-td :props="props" class="text-weight-bold">PHP {{ format(props.row.amount) }}</q-td></template>
          <template #body-cell-status="props"><q-td :props="props"><q-badge color="positive">{{ props.row.status }}</q-badge></q-td></template>
        </q-table>
      </section>
    </div>
    <q-dialog v-model="reviewOpen" persistent><q-card style="width:440px;max-width:95vw"><q-card-section><h2 class="section-heading">Confirm bill payment</h2><p>{{ form.biller_name }} · {{ form.biller_reference }}</p><div class="goal-amount">₱ {{ format(form.amount) }}</div><p class="page-subtitle">This simulated payment will be deducted from your available balance.</p></q-card-section><q-card-actions align="right"><q-btn flat label="Go back" :disable="submitting" v-close-popup /><q-btn color="primary" label="Confirm payment" :loading="submitting" @click="payBill" /></q-card-actions></q-card></q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const accounts = ref([])
const payments = ref([])
const loading = ref(true)
const submitting = ref(false)
const reviewOpen = ref(false)
const errorMessage = ref('')
const form = ref({ account_id: null, biller_name: '', biller_reference: '', amount: null })
const accountOptions = computed(() => accounts.value
  .filter((account) => account.status === 'ACTIVE')
  .map((account) => ({ label: `${account.account_number} · PHP ${format(account.available_balance)}`, value: account.id })))
const columns = [
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left', sortable: true },
  { name: 'biller_name', label: 'Biller', field: 'biller_name', align: 'left' },
  { name: 'biller_reference', label: 'Reference', field: 'biller_reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
]

function format (value) {
  return Number(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData () {
  loading.value = true
  errorMessage.value = ''
  try {
    const [accountResponse, paymentResponse] = await Promise.all([
      api.get('/customer/accounts/'),
      api.get('/customer/bill-payments/'),
    ])
    accounts.value = accountResponse.data
    payments.value = paymentResponse.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load bill payment data.'
  } finally {
    loading.value = false
  }
}

async function payBill () {
  if (submitting.value) return
  submitting.value = true
  try {
    await api.post('/customer/bill-payments/', form.value)
    reviewOpen.value = false
    form.value = { account_id: null, biller_name: '', biller_reference: '', amount: null }
    $q.notify({ type: 'positive', message: 'Payment recorded' })
    await loadData()
  } catch (error) {
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Payment could not be recorded.' })
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>
