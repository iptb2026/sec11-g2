<template>
  <div>
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">Transaction History</div>
        <div class="text-caption text-grey">Review past deposits, withdrawals, and transfers on your accounts</div>
      </div>
      <q-select
        v-if="myAccounts.length > 0"
        v-model="selectedAccountId"
        :options="accountFilterOptions"
        label="Filter by Account"
        outlined
        dense
        emit-value
        map-options
        style="min-width: 220px"
        @update:model-value="fetchTransactions"
      />
    </div>

    <!-- Tabs for transaction types -->
    <q-card flat bordered>
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="deep-purple-8"
        indicator-color="deep-purple-8"
        align="left"
      >
        <q-tab name="all" label="All Activity" icon="swap_horiz" />
        <q-tab name="deposits" label="Deposits" icon="savings" />
        <q-tab name="withdrawals" label="Withdrawals" icon="money_off" />
        <q-tab name="transfers" label="Transfers" icon="sync_alt" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="activeTab" animated>
        <!-- ALL ACTIVITY -->
        <q-tab-panel name="all" class="q-pa-none">
          <q-table
            :rows="allTransactions"
            :columns="allColumns"
            row-key="key"
            :loading="loading"
            flat
            dense
            no-data-label="No transactions found for your accounts."
          >
            <template v-slot:body-cell-type="props">
              <q-td :props="props">
                <q-chip
                  dense
                  size="sm"
                  :color="getTypeChipColor(props.row.type)"
                  text-color="white"
                >
                  {{ props.row.type }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-amount="props">
              <q-td :props="props" class="text-right text-weight-bold" :class="props.row.isCredit ? 'text-positive' : 'text-negative'">
                {{ props.row.isCredit ? '+' : '-' }}₱{{ Number(props.row.amount).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- DEPOSITS -->
        <q-tab-panel name="deposits" class="q-pa-none">
          <q-table
            :rows="deposits"
            :columns="depositColumns"
            row-key="id"
            :loading="loading"
            flat
            dense
            no-data-label="No deposit records found."
          >
            <template v-slot:body-cell-amount="props">
              <q-td :props="props" class="text-right text-positive text-weight-bold">
                +₱{{ Number(props.row.amount).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- WITHDRAWALS -->
        <q-tab-panel name="withdrawals" class="q-pa-none">
          <q-table
            :rows="withdrawals"
            :columns="withdrawalColumns"
            row-key="id"
            :loading="loading"
            flat
            dense
            no-data-label="No withdrawal records found."
          >
            <template v-slot:body-cell-amount="props">
              <q-td :props="props" class="text-right text-negative text-weight-bold">
                -₱{{ Number(props.row.amount).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- TRANSFERS -->
        <q-tab-panel name="transfers" class="q-pa-none">
          <q-table
            :rows="transfers"
            :columns="transferColumns"
            row-key="id"
            :loading="loading"
            flat
            dense
            no-data-label="No transfer records found."
          >
            <template v-slot:body-cell-amount="props">
              <q-td :props="props" class="text-right text-weight-bold">
                ₱{{ Number(props.row.amount).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '../../api'

const $q = useQuasar()
const activeTab = ref('all')
const loading = ref(false)
const myAccounts = ref([])
const selectedAccountId = ref(null)

const deposits = ref([])
const withdrawals = ref([])
const transfers = ref([])

const accountFilterOptions = computed(() => {
  return [
    { label: 'All My Accounts', value: null },
    ...myAccounts.value.map(acc => ({
      label: `${acc.account_number} (ID: ${acc.id})`,
      value: acc.id,
    })),
  ]
})

const allColumns = [
  { name: 'date', label: 'Date', field: 'date', align: 'left', format: v => v ? new Date(v).toLocaleString() : '' },
  { name: 'type', label: 'Type', field: 'type', align: 'center' },
  { name: 'reference', label: 'Reference', field: 'reference', align: 'left' },
  { name: 'account', label: 'Account ID', field: 'accountId', align: 'center' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
]

const depositColumns = [
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left', format: v => v ? new Date(v).toLocaleString() : '' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'center' },
  { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel', align: 'center' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'remarks', label: 'Remarks', field: 'remarks', align: 'left' },
]

const withdrawalColumns = [
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left', format: v => v ? new Date(v).toLocaleString() : '' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'center' },
  { name: 'withdrawal_channel', label: 'Channel', field: 'withdrawal_channel', align: 'center' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'remarks', label: 'Remarks', field: 'remarks', align: 'left' },
]

const transferColumns = [
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left', format: v => v ? new Date(v).toLocaleString() : '' },
  { name: 'transfer_reference', label: 'Reference', field: 'transfer_reference', align: 'left' },
  { name: 'source_account_id', label: 'From Account', field: 'source_account_id', align: 'center' },
  { name: 'destination_account_id', label: 'To Account', field: 'destination_account_id', align: 'center' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
]

const allTransactions = computed(() => {
  const list = []
  deposits.value.forEach(d => {
    list.push({
      key: 'dep-' + d.id,
      date: d.transaction_date,
      type: 'DEPOSIT',
      reference: d.reference_number,
      accountId: d.account_id,
      amount: d.amount,
      isCredit: true,
    })
  })
  withdrawals.value.forEach(w => {
    list.push({
      key: 'wth-' + w.id,
      date: w.transaction_date,
      type: 'WITHDRAWAL',
      reference: w.reference_number,
      accountId: w.account_id,
      amount: w.amount,
      isCredit: false,
    })
  })
  transfers.value.forEach(t => {
    const isSender = myAccounts.value.some(a => a.id === t.source_account_id)
    list.push({
      key: 'trf-' + t.id,
      date: t.created_at,
      type: 'TRANSFER',
      reference: t.transfer_reference,
      accountId: isSender ? t.source_account_id : t.destination_account_id,
      amount: t.amount,
      isCredit: !isSender,
    })
  })
  list.sort((a, b) => new Date(b.date) - new Date(a.date))
  return list
})

function getTypeChipColor(type) {
  if (type === 'DEPOSIT') return 'green'
  if (type === 'WITHDRAWAL') return 'red'
  return 'deep-purple'
}

async function fetchTransactions() {
  loading.value = true
  try {
    const myAccIds = myAccounts.value.map(a => a.id)
    if (myAccIds.length === 0) {
      deposits.value = []
      withdrawals.value = []
      transfers.value = []
      return
    }

    if (selectedAccountId.value) {
      const [depRes, wthRes, trfRes] = await Promise.all([
        api.get(`/deposits/?account_id=${selectedAccountId.value}`),
        api.get(`/withdrawals/?account_id=${selectedAccountId.value}`),
        api.get(`/transfers/?account_id=${selectedAccountId.value}`),
      ])
      deposits.value = depRes.data
      withdrawals.value = wthRes.data
      transfers.value = trfRes.data
    } else {
      // Aggregate across all own accounts
      const depPromises = myAccIds.map(id => api.get(`/deposits/?account_id=${id}`))
      const wthPromises = myAccIds.map(id => api.get(`/withdrawals/?account_id=${id}`))
      const trfPromises = myAccIds.map(id => api.get(`/transfers/?account_id=${id}`))

      const [allDeps, allWths, allTrfs] = await Promise.all([
        Promise.all(depPromises),
        Promise.all(wthPromises),
        Promise.all(trfPromises),
      ])

      deposits.value = allDeps.flatMap(r => r.data).filter((v, i, a) => a.findIndex(t => t.id === v.id) === i)
      withdrawals.value = allWths.flatMap(r => r.data).filter((v, i, a) => a.findIndex(t => t.id === v.id) === i)
      transfers.value = allTrfs.flatMap(r => r.data).filter((v, i, a) => a.findIndex(t => t.id === v.id) === i)
    }
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load transaction history',
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/accounts/my')
    myAccounts.value = data
    await fetchTransactions()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'Failed to initialize account list',
    })
  }
})
</script>
