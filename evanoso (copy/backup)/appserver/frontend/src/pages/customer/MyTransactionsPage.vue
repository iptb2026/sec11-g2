<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">My Transactions</div>

    <q-table
      :rows="rows"
      :columns="columns"
      row-key="key"
      :loading="loading"
      flat
      bordered
      :pagination="{ sortBy: 'date', descending: true, rowsPerPage: 15 }"
    >
      <template #body-cell-type="props">
        <q-td :props="props">
          <q-badge :color="badgeColor(props.row.type)">{{ props.row.type }}</q-badge>
        </q-td>
      </template>
      <template #body-cell-amount="props">
        <q-td :props="props" :class="props.row.direction === 'credit' ? 'text-positive' : 'text-negative'">
          {{ props.row.direction === 'credit' ? '+' : '-' }}₱{{ format(props.row.amount) }}
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const rows = ref([])
const loading = ref(true)

const columns = [
  { name: 'account_number', label: 'Account Number', field: 'account_number', align: 'left' },
  { name: 'date', label: 'Date', field: 'date', align: 'left', sortable: true },
  { name: 'type', label: 'Type', field: 'type', align: 'left' },
  { name: 'reference', label: 'Reference', field: 'reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
]

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function badgeColor (type) {
  return {
    DEPOSIT: 'positive',
    WITHDRAWAL: 'negative',
    'TRANSFER OUT': 'negative',
    'TRANSFER IN': 'positive',
    INTERBANK: 'negative',
  }[type] || 'grey'
}

onMounted(async () => {
  try {
    const { data: allAccounts } = await api.get('/accounts/')
    const myAccountIds = allAccounts.filter((a) => a.customer_id === auth.userId).map((a) => a.id)
    const accountNumberById = Object.fromEntries(allAccounts.map((a) => [a.id, a.account_number]))

    const [deposits, withdrawals, transfers, interbank] = await Promise.all([
      api.get('/deposits/'),
      api.get('/withdrawals/'),
      api.get('/transfers/'),
      api.get('/interbank-transfers/'),
    ])

    const combined = []

    for (const d of deposits.data) {
      if (myAccountIds.includes(d.account_id)) {
        combined.push({
          key: `dep-${d.id}`,
          date: d.transaction_date,
          type: 'DEPOSIT',
          account_number: accountNumberById[d.account_id],
          reference: d.reference_number,
          amount: d.amount,
          direction: 'credit',
        })
      }
    }

    for (const w of withdrawals.data) {
      if (myAccountIds.includes(w.account_id)) {
        combined.push({
          key: `wd-${w.id}`,
          date: w.transaction_date,
          type: 'WITHDRAWAL',
          account_number: accountNumberById[w.account_id],
          reference: w.reference_number,
          amount: w.amount,
          direction: 'debit',
        })
      }
    }

    for (const t of transfers.data) {
      if (myAccountIds.includes(t.source_account_id)) {
        combined.push({
          key: `trf-out-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER OUT',
          account_number: accountNumberById[t.source_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'debit',
        })
      }
      if (myAccountIds.includes(t.destination_account_id)) {
        combined.push({
          key: `trf-in-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER IN',
          account_number: accountNumberById[t.destination_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'credit',
        })
      }
    }

    for (const i of interbank.data) {
      if (myAccountIds.includes(i.source_account_id)) {
        combined.push({
          key: `ibt-${i.id}`,
          date: i.initiated_at,
          type: 'INTERBANK',
          account_number: accountNumberById[i.source_account_id],
          reference: i.reference_number,
          amount: Number(i.amount) + Number(i.transfer_fee),
          direction: 'debit',
        })
      }
    }

    combined.sort((a, b) => new Date(b.date) - new Date(a.date))
    rows.value = combined
  } finally {
    loading.value = false
  }
})
</script>
