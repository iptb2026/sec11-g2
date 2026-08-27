<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h4 text-weight-bolder text-primary">My Accounts</div>
        <div class="text-subtitle1 text-grey-7">Welcome back, {{ authStore.fullName || authStore.username }}!</div>
      </div>
      <div class="q-gutter-sm">
        <q-btn color="primary" icon="swap_horiz" label="Transfer Money" unelevated @click="openTransfer" />
        <q-btn color="secondary" icon="send" label="Send to Other Bank" outline @click="openInterbank" />
      </div>
    </div>

    <!-- Total Net Worth Banner -->
    <q-card class="bg-gradient q-pa-lg text-white q-mb-lg shadow-3" style="background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%); border-radius: 16px;">
      <div class="row items-center justify-between">
        <div>
          <div class="text-caption text-blue-2 text-uppercase text-weight-bold">Total Available Portfolio</div>
          <div class="text-h3 text-weight-bolder q-mt-xs">
            ₱{{ Number(totalBalance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
          </div>
          <div class="text-caption text-blue-1 q-mt-xs">
            Active Accounts: {{ accounts.length }} | PHP Currency
          </div>
        </div>
        <q-icon name="account_balance_wallet" size="64px" color="blue-2" style="opacity: 0.8" />
      </div>
    </q-card>

    <!-- Account Cards Grid -->
    <div class="text-h6 text-weight-bold q-mb-md">Your Accounts</div>
    <div v-if="loading" class="row justify-center q-pa-xl">
      <q-spinner color="primary" size="48px" />
    </div>

    <div v-else-if="accounts.length === 0" class="q-pa-xl text-center text-grey-7">
      <q-icon name="credit_card_off" size="64px" class="q-mb-sm" />
      <div class="text-h6">No accounts found</div>
      <div class="text-caption">Please visit a branch or contact support to open an account.</div>
    </div>

    <div v-else class="row q-col-gutter-md">
      <div v-for="acc in accounts" :key="acc.id" class="col-12 col-md-6 col-lg-4">
        <q-card bordered flat class="account-card full-height" style="border-radius: 12px;">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <q-badge color="blue-9" class="q-py-xs q-px-sm text-weight-bold">
                {{ accountTypeNameById[acc.account_type_id] || 'Deposit Account' }}
              </q-badge>
              <q-badge :color="acc.status === 'ACTIVE' ? 'positive' : 'negative'">
                {{ acc.status }}
              </q-badge>
            </div>
            <div class="text-h6 text-weight-bolder text-mono text-grey-9 q-mt-sm">
              {{ acc.account_number }}
            </div>
            <div class="text-caption text-grey-6">Branch: {{ acc.branch_code || 'Main Metro' }}</div>
          </q-card-section>

          <q-separator />

          <q-card-section class="bg-grey-1">
            <div class="text-caption text-grey-7">Available Balance</div>
            <div class="text-h5 text-weight-bold text-primary">
              ₱{{ Number(acc.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">
              Ledger Balance: ₱{{ Number(acc.ledger_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
            </div>
          </q-card-section>

          <q-card-actions align="between" class="q-pa-md">
            <q-btn flat dense color="primary" icon="history" label="View History" to="/my-transactions" />
            <q-btn flat dense color="secondary" icon="swap_horiz" label="Transfer" @click="openTransferFrom(acc)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Quick Transfer Dialog -->
    <q-dialog v-model="showTransferDialog" persistent>
      <q-card style="min-width: 450px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Transfer Funds</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="executeTransfer">
          <q-card-section class="q-gutter-md">
            <q-select
              v-model="transferForm.source_account_id"
              :options="myAccountOptions"
              label="From Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Source account is required']"
            />
            <q-select
              v-model="transferForm.destination_account_id"
              :options="allAccountOptions"
              label="To Destination Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Destination account is required', val => val !== transferForm.source_account_id || 'Cannot transfer to same account']"
            />
            <q-input
              v-model.number="transferForm.amount"
              label="Amount (₱) *"
              type="number"
              step="0.01"
              filled
              :rules="[val => val > 0 || 'Amount must be greater than zero']"
            />
            <q-input
              v-model="transferForm.remarks"
              label="Note / Purpose"
              filled
            />
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" label="Send Transfer" :loading="submitting" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- Quick Interbank Dialog -->
    <q-dialog v-model="showInterbankDialog" persistent>
      <q-card style="min-width: 480px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Send Money to Other Bank (InstaPay)</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="executeInterbank">
          <q-card-section class="q-gutter-md">
            <q-select
              v-model="interbankForm.source_account_id"
              :options="myAccountOptions"
              label="From My Account *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Source required']"
            />
            <q-select
              v-model="interbankForm.target_bank_id"
              :options="bankOptions"
              label="Receiving Bank *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Bank required']"
            />
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="interbankForm.target_account_number"
                  label="Target Account Number *"
                  filled
                  :rules="[val => !!val || 'Target account required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="interbankForm.beneficiary_name"
                  label="Recipient Full Name *"
                  filled
                  :rules="[val => !!val || 'Recipient name required']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-8">
                <q-input
                  v-model.number="interbankForm.amount"
                  label="Amount (₱) *"
                  type="number"
                  step="0.01"
                  filled
                  :rules="[val => val > 0 || 'Amount must be > 0']"
                />
              </div>
              <div class="col-4">
                <q-input
                  v-model.number="interbankForm.transfer_fee"
                  label="Fee (₱)"
                  type="number"
                  filled
                  disable
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="secondary" label="Confirm Send" :loading="submitting" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'

const $q = useQuasar()
const authStore = useAuthStore()

const accounts = ref([])
const allAccounts = ref([])
const bankOptions = ref([])
const accountTypeNameById = ref({})
const loading = ref(false)
const submitting = ref(false)
const showTransferDialog = ref(false)
const showInterbankDialog = ref(false)

const transferForm = ref({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: '',
  amount: 500,
  transfer_type: 'INTERNAL',
  remarks: '',
})

const interbankForm = ref({
  source_account_id: null,
  target_bank_id: null,
  target_account_number: '',
  beneficiary_name: '',
  reference_number: '',
  amount: 1000,
  transfer_fee: 25,
})

const totalBalance = computed(() => {
  return accounts.value.reduce((sum, a) => sum + Number(a.available_balance || 0), 0)
})

const myAccountOptions = computed(() => {
  return accounts.value.map(a => ({
    label: `${a.account_number} (₱${Number(a.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`,
    value: a.id,
  }))
})

const allAccountOptions = computed(() => {
  return allAccounts.value.map(a => ({
    label: `${a.account_number}`,
    value: a.id,
  }))
})

async function loadData () {
  loading.value = true
  try {
    const [accRes, actRes, bankRes] = await Promise.all([
      api.get('/accounts/'),
      api.get('/account-types/'),
      api.get('/banks/'),
    ])
    // The backend /accounts/ endpoint for CUSTOMER already filters to own accounts!
    accounts.value = accRes.data
    allAccounts.value = accRes.data

    const actMap = {}
    actRes.data.forEach(a => { actMap[a.id] = a.type_name })
    accountTypeNameById.value = actMap

    bankOptions.value = bankRes.data.map(b => ({ label: `${b.bank_name} (${b.bank_code})`, value: b.id }))
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load accounts' })
  } finally {
    loading.value = false
  }
}

function openTransfer () {
  transferForm.value = {
    source_account_id: accounts.value[0]?.id || null,
    destination_account_id: null,
    transfer_reference: `TRF-${Date.now().toString().slice(-6)}`,
    amount: 500,
    transfer_type: 'INTERNAL',
    remarks: 'Self transfer',
  }
  showTransferDialog.value = true
}

function openTransferFrom (acc) {
  transferForm.value = {
    source_account_id: acc.id,
    destination_account_id: null,
    transfer_reference: `TRF-${Date.now().toString().slice(-6)}`,
    amount: 500,
    transfer_type: 'INTERNAL',
    remarks: 'Self transfer',
  }
  showTransferDialog.value = true
}

function openInterbank () {
  interbankForm.value = {
    source_account_id: accounts.value[0]?.id || null,
    target_bank_id: bankOptions.value[0]?.value || null,
    target_account_number: '',
    beneficiary_name: '',
    reference_number: `IBT-${Date.now().toString().slice(-6)}`,
    amount: 1000,
    transfer_fee: 25,
  }
  showInterbankDialog.value = true
}

async function executeTransfer () {
  submitting.value = true
  try {
    await api.post('/transfers/', transferForm.value)
    $q.notify({ type: 'positive', message: 'Transfer completed successfully' })
    showTransferDialog.value = false
    await loadData()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Transfer failed' })
  } finally {
    submitting.value = false
  }
}

async function executeInterbank () {
  submitting.value = true
  try {
    await api.post('/interbank-transfers/', interbankForm.value)
    $q.notify({ type: 'positive', message: 'Interbank transfer sent successfully' })
    showInterbankDialog.value = false
    await loadData()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Transfer failed' })
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.account-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.account-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}
</style>
