<template>
  <q-page class="customer-flow-page history-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow">Customer banking</div>
        <h1 class="page-title">Transactions</h1>
        <p class="page-subtitle">Your account activity in one place.</p>
      </div>
    </div>

    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">
      {{ errorMessage }}
    </q-banner>

    <div class="transaction-filters q-mb-lg"><q-input v-model="search" filled dense placeholder="Search transactions" aria-label="Search transactions"><template #prepend><q-icon name="search" /></template></q-input><q-select v-model="direction" filled dense :options="['All activity', 'Money in', 'Money out', 'Transfers']" label="Transaction filter" /><DatePickerField v-model="fromDate" filled dense label="From date" clearable /><DatePickerField v-model="toDate" filled dense label="To date" clearable /><q-btn outline color="primary" icon="download" label="Export CSV" :disable="!filtered.length" @click="exportCsv" /></div>
    <div class="mobile-history">
      <div class="history-tabs"><q-btn v-for="tab in historyTabs" :key="tab.value" flat :label="tab.label" :class="{ selected: direction === tab.value }" @click="direction = tab.value" /></div>
      <q-spinner v-if="loading" color="primary" />
      <q-list v-else><q-item v-for="item in filtered" :key="item.id" clickable @click="receipt(item)"><q-item-section avatar><q-avatar :class="item.direction === 'CREDIT' ? 'income-icon' : 'expense-icon'" rounded><q-icon :name="item.direction === 'CREDIT' ? 'south_west' : 'north_east'" /></q-avatar></q-item-section><q-item-section><q-item-label>{{ item.transaction_type.replaceAll('_', ' ').toLowerCase() }}</q-item-label><q-item-label caption>{{ new Date(item.transaction_date).toLocaleString('en-PH', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) }}</q-item-label></q-item-section><q-item-section side :class="item.direction === 'CREDIT' ? 'text-positive' : 'text-negative'">{{ item.direction === 'CREDIT' ? '+' : '−' }}₱{{ format(item.amount) }}</q-item-section></q-item></q-list>
      <p v-if="!loading && !filtered.length" class="page-subtitle q-pa-md">No transactions match your filters.</p>
    </div>
    <q-table
      :rows="filtered"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
      :pagination="{ sortBy: 'transaction_date', descending: true, rowsPerPage: 15 }"
    >
      <template #body-cell-transaction_type="props">
        <q-td :props="props">
          <q-badge :color="badgeColor(props.row.transaction_type)">{{ props.row.transaction_type }}</q-badge>
        </q-td>
      </template>
      <template #body-cell-receipt="props"><q-td :props="props"><q-btn flat round icon="download" aria-label="Download receipt" @click="receipt(props.row)" /></q-td></template>
      <template #body-cell-amount="props">
        <q-td :props="props" :class="props.row.direction === 'CREDIT' ? 'text-positive' : 'text-negative'">
          {{ props.row.direction === 'CREDIT' ? '+' : '-' }} PHP {{ format(props.row.amount) }}
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import DatePickerField from '@/components/DatePickerField.vue'
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const rows = ref([])
const loading = ref(true)
const errorMessage = ref('')
const search = ref(''), direction = ref('All activity'), fromDate = ref(''), toDate = ref('')
const historyTabs = [{ label: 'All', value: 'All activity' }, { label: 'Income', value: 'Money in' }, { label: 'Expense', value: 'Money out' }, { label: 'Transfers', value: 'Transfers' }]
const filtered = computed(() => rows.value.filter(row => (!search.value || `${row.reference} ${row.account_number} ${row.transaction_type}`.toLowerCase().includes(search.value.toLowerCase())) && (direction.value === 'All activity' || (direction.value === 'Transfers' ? row.transaction_type.includes('TRANSFER') : row.direction === (direction.value === 'Money in' ? 'CREDIT' : 'DEBIT'))) && (!fromDate.value || row.transaction_date.slice(0, 10) >= fromDate.value) && (!toDate.value || row.transaction_date.slice(0, 10) <= toDate.value)).sort((a, b) => new Date(b.transaction_date) - new Date(a.transaction_date)))
function download (text, name, type) { const url = URL.createObjectURL(new Blob([text], { type })); const a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000) }
function receipt (row) { download(`BEMBANK\nSIMULATED TRANSACTION RECEIPT\n\nReference: ${row.reference}\nDate: ${row.transaction_date}\nAccount: ${row.account_number}\nType: ${row.transaction_type}\nDirection: ${row.direction}\nAmount: PHP ${format(row.amount)}\nStatus: ${row.status}\n\nNo real money was moved.`, `bembank-receipt-${row.id}.txt`, 'text/plain') }
function exportCsv () { const fields = ['transaction_date', 'reference', 'account_number', 'transaction_type', 'direction', 'amount', 'status']; const cell = value => { let s = String(value ?? ''); if (/^[=+@\-\t\r]/.test(s)) s = "'" + s; return '"' + s.replaceAll('"', '""') + '"' }; download([fields.join(','), ...filtered.value.map(row => fields.map(key => cell(row[key])).join(','))].join('\r\n'), 'bembank-transactions.csv', 'text/csv;charset=utf-8') }

const columns = [
  { name: 'receipt', label: 'Receipt', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: 'account_number', align: 'left' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left', sortable: true },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'reference', label: 'Reference', field: 'reference', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
]

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function badgeColor (type) {
  return {
    DEPOSIT: 'positive',
    'TRANSFER IN': 'positive',
    'INVESTMENT REDEMPTION': 'positive',
    WITHDRAWAL: 'negative',
    'TRANSFER OUT': 'negative',
    'INTERBANK TRANSFER': 'negative',
    'BILL PAYMENT': 'negative',
    'INVESTMENT ALLOCATION': 'warning',
  }[type] || 'grey'
}

onMounted(async () => {
  try {
    const { data } = await api.get('/customer/transactions/')
    rows.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load your transactions.'
  } finally {
    loading.value = false
  }
})
</script>
