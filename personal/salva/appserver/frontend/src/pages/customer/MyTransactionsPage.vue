<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h4 text-weight-bolder text-primary">Transaction History</div>
        <div class="text-caption text-grey-7">Comprehensive activity log of all account deposits, withdrawals, and transfers</div>
      </div>
      <q-btn color="primary" icon="refresh" label="Refresh" outline @click="loadTimeline" />
    </div>

    <!-- Filters -->
    <q-card bordered flat class="q-mb-md q-pa-md">
      <div class="row q-col-gutter-md items-center">
        <div class="col-12 col-md-4">
          <q-select
            v-model="selectedAccountId"
            :options="accountFilterOptions"
            label="Filter by Account"
            filled
            emit-value
            map-options
            clearable
          />
        </div>
        <div class="col-12 col-md-4">
          <q-select
            v-model="selectedType"
            :options="['ALL', 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'INTERBANK']"
            label="Transaction Type"
            filled
          />
        </div>
        <div class="col-12 col-md-4">
          <q-input
            v-model="searchQuery"
            label="Search reference or memo"
            filled
            clearable
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>
      </div>
    </q-card>

    <!-- Timeline List -->
    <div v-if="loading" class="row justify-center q-pa-xl">
      <q-spinner color="primary" size="48px" />
    </div>

    <div v-else-if="filteredTransactions.length === 0" class="q-pa-xl text-center text-grey-7">
      <q-icon name="receipt_long" size="64px" class="q-mb-sm" />
      <div class="text-h6">No transactions found</div>
      <div class="text-caption">Try adjusting your filters or search query.</div>
    </div>

    <q-card v-else bordered flat>
      <q-list separator>
        <q-item v-for="tx in filteredTransactions" :key="tx.uniqueKey" class="q-py-md">
          <q-item-section avatar>
            <q-avatar :color="getTxColor(tx.type)" text-color="white" :icon="getTxIcon(tx.type)" />
          </q-item-section>

          <q-item-section>
            <div class="row items-center q-gutter-x-sm">
              <span class="text-weight-bold text-subtitle1">{{ tx.title }}</span>
              <q-badge :color="getTxColor(tx.type)" outline>{{ tx.type }}</q-badge>
              <q-badge v-if="tx.status" :color="tx.status === 'SUCCESS' ? 'positive' : 'warning'">{{ tx.status }}</q-badge>
            </div>
            <div class="text-caption text-grey-7 q-mt-xs">
              Ref: <span class="text-mono text-weight-medium">{{ tx.reference }}</span> | {{ tx.accountLabel }}
            </div>
            <div v-if="tx.remarks" class="text-caption text-grey-6 italic">
              "{{ tx.remarks }}"
            </div>
          </q-item-section>

          <q-item-section side class="text-right">
            <div class="text-h6 text-weight-bolder" :class="tx.isCredit ? 'text-positive' : 'text-negative'">
              {{ tx.isCredit ? '+' : '-' }}₱{{ Number(tx.amount).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
            </div>
            <div class="text-caption text-grey-6">
              {{ new Date(tx.timestamp).toLocaleString() }}
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const loading = ref(false)
const accounts = ref([])
const accountNumberById = ref({})
const rawTransactions = ref([])

const selectedAccountId = ref(null)
const selectedType = ref('ALL')
const searchQuery = ref('')

const accountFilterOptions = computed(() => {
  return [
    { label: 'All Accounts', value: null },
    ...accounts.value.map(a => ({
      label: a.account_number,
      value: a.id,
    })),
  ]
})

function getTxColor (type) {
  if (type === 'DEPOSIT') return 'positive'
  if (type === 'WITHDRAWAL') return 'deep-orange'
  if (type === 'TRANSFER') return 'primary'
  if (type === 'INTERBANK') return 'indigo'
  return 'grey-8'
}

function getTxIcon (type) {
  if (type === 'DEPOSIT') return 'savings'
  if (type === 'WITHDRAWAL') return 'payments'
  if (type === 'TRANSFER') return 'swap_horiz'
  if (type === 'INTERBANK') return 'send'
  return 'receipt'
}

async function loadTimeline () {
  loading.value = true
  try {
    const [accRes, depRes, wthRes, trfRes, ibtRes] = await Promise.all([
      api.get('/accounts/'),
      api.get('/deposits/'),
      api.get('/withdrawals/'),
      api.get('/transfers/'),
      api.get('/interbank-transfers/'),
    ])

    accounts.value = accRes.data
    const accMap = {}
    accRes.data.forEach(a => { accMap[a.id] = a.account_number })
    accountNumberById.value = accMap

    const txList = []

    // Deposits (Credits)
    depRes.data.forEach(d => {
      txList.push({
        uniqueKey: `dep-${d.id}`,
        type: 'DEPOSIT',
        title: `Deposit via ${d.deposit_channel}`,
        reference: d.reference_number,
        accountId: d.account_id,
        accountLabel: `Account: ${accMap[d.account_id] || `#${d.account_id}`}`,
        amount: Number(d.amount),
        isCredit: true,
        remarks: d.remarks,
        timestamp: d.created_at || d.transaction_date,
      })
    })

    // Withdrawals (Debits)
    wthRes.data.forEach(w => {
      txList.push({
        uniqueKey: `wth-${w.id}`,
        type: 'WITHDRAWAL',
        title: `Withdrawal via ${w.withdrawal_channel}`,
        reference: w.reference_number,
        accountId: w.account_id,
        accountLabel: `Account: ${accMap[w.account_id] || `#${w.account_id}`}`,
        amount: Number(w.amount),
        isCredit: false,
        remarks: w.remarks,
        timestamp: w.created_at || w.transaction_date,
      })
    })

    // Transfers
    trfRes.data.forEach(t => {
      const isOutward = accounts.value.some(a => a.id === t.source_account_id)
      const isInward = accounts.value.some(a => a.id === t.destination_account_id)

      if (isOutward) {
        txList.push({
          uniqueKey: `trf-out-${t.id}`,
          type: 'TRANSFER',
          title: `Transfer to ${accMap[t.destination_account_id] || `Account #${t.destination_account_id}`}`,
          reference: t.transfer_reference,
          accountId: t.source_account_id,
          accountLabel: `From: ${accMap[t.source_account_id]} -> To: ${accMap[t.destination_account_id] || `#${t.destination_account_id}`}`,
          amount: Number(t.amount),
          isCredit: false,
          status: t.status,
          remarks: t.remarks,
          timestamp: t.created_at,
        })
      }
      if (isInward && t.source_account_id !== t.destination_account_id) {
        txList.push({
          uniqueKey: `trf-in-${t.id}`,
          type: 'TRANSFER',
          title: `Transfer from ${accMap[t.source_account_id] || `Account #${t.source_account_id}`}`,
          reference: t.transfer_reference,
          accountId: t.destination_account_id,
          accountLabel: `From: ${accMap[t.source_account_id] || `#${t.source_account_id}`} -> To: ${accMap[t.destination_account_id]}`,
          amount: Number(t.amount),
          isCredit: true,
          status: t.status,
          remarks: t.remarks,
          timestamp: t.created_at,
        })
      }
    })

    // Interbank Transfers
    ibtRes.data.forEach(ibt => {
      txList.push({
        uniqueKey: `ibt-${ibt.id}`,
        type: 'INTERBANK',
        title: `Outward Transfer to ${ibt.beneficiary_name || 'Payee'}`,
        reference: ibt.reference_number,
        accountId: ibt.source_account_id,
        accountLabel: `From: ${accMap[ibt.source_account_id]} -> Ext #${ibt.target_account_number}`,
        amount: Number(ibt.amount),
        isCredit: false,
        status: ibt.status,
        remarks: `Fee: ₱${Number(ibt.transfer_fee).toFixed(2)}`,
        timestamp: ibt.initiated_at,
      })
    })

    // Sort descending by timestamp
    txList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    rawTransactions.value = txList
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load transactions' })
  } finally {
    loading.value = false
  }
}

const filteredTransactions = computed(() => {
  return rawTransactions.value.filter(tx => {
    if (selectedAccountId.value && tx.accountId !== selectedAccountId.value) {
      return false
    }
    if (selectedType.value !== 'ALL' && tx.type !== selectedType.value) {
      return false
    }
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchRef = tx.reference?.toLowerCase().includes(q)
      const matchRem = tx.remarks?.toLowerCase().includes(q)
      const matchTitle = tx.title?.toLowerCase().includes(q)
      if (!matchRef && !matchRem && !matchTitle) return false
    }
    return true
  })
})

onMounted(loadTimeline)
</script>
