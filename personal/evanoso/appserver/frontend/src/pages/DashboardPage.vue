<template>
  <q-page class="dashboard-page" :class="{ 'customer-dashboard': auth.isCustomer }">
    <div class="page-heading">
      <div>
        <div class="eyebrow">{{ auth.isCustomer ? 'PERSONAL BANKING' : auth.isAdmin ? 'BANK ADMINISTRATION' : 'BRANCH OPERATIONS' }}</div>
        <h1 class="page-title">Welcome back, {{ displayName }} <span class="greeting-dot">✦</span></h1>
        <p class="page-subtitle">{{ dashboardSubtitle }}</p>
      </div>
      <div class="dashboard-date">{{ today }}</div>
    </div>

    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">
      {{ errorMessage }}
    </q-banner>

    <div v-if="loading" class="dashboard-loading">
      <q-spinner color="primary" size="32px" />
      <span>Loading workspace data</span>
    </div>

    <template v-else>
      <section v-if="auth.isCustomer" class="balance-hero overview-hero"><div class="row items-center justify-between"><span>Total available balance</span><q-btn flat round size="sm" :icon="hidden ? 'visibility_off' : 'visibility'" :aria-label="hidden ? 'Show balance' : 'Hide balance'" @click="hidden = !hidden" /></div><div class="hero-amount">{{ hidden ? '••••••' : formatCurrency(balance) }}</div><div class="balance-caption">Across {{ customerAccounts.length }} Bembank accounts</div><div class="hero-bottom"><span><span class="status-dot" /> Your everyday essentials, connected</span><BankLogo /></div></section>
      <div v-if="auth.isCustomer" class="mobile-dashboard-actions">
        <div class="mobile-primary-actions"><q-btn v-for="action in mobilePrimaryActions" :key="action.label" flat stack :icon="action.icon" :label="action.label" :to="action.to" /></div>
        <h2 class="section-heading">Quick Actions</h2>
        <CustomerActionGrid />
      </div>
      <section class="metric-grid" aria-label="Summary metrics">
        <q-card v-for="card in cards" :key="card.label" flat bordered class="metric-card">
          <div class="metric-card-inner">
            <div class="metric-topline">
              <span>{{ card.label }}</span>
              <span class="metric-icon"><q-icon :name="card.icon" size="18px" /></span>
            </div>
            <div class="metric-value">{{ hidden && auth.isCustomer ? '••••' : card.value }}</div>
            <p class="metric-context">{{ card.context }}</p>
            <q-btn
              v-if="card.to"
              flat
              dense
              no-caps
              icon-right="arrow_forward"
              label="View details"
              class="metric-link"
              :to="card.to"
            />
          </div>
        </q-card>
      </section>

      <section v-if="!auth.isCustomer" class="dashboard-section overview-chart">
        <div><div class="eyebrow">ACCOUNT HEALTH</div><h2 class="section-heading">Account status</h2><p class="page-subtitle">A quick view of accounts available for banking versus accounts needing attention.</p></div>
        <div class="cash-flow-chart"><div class="cash-flow-pie" :style="accountStatusChartStyle" role="img" :aria-label="accountStatusChartLabel"><div><strong>{{ accountStatusTotal ? `${activeAccountPercent}%` : '—' }}</strong><span>active</span></div></div><div class="cash-flow-legend"><div><span class="cash-flow-key money-in" /><span>Active accounts</span><strong>{{ accountStatus.active }}</strong></div><div><span class="cash-flow-key money-out" /><span>Needs attention</span><strong>{{ accountStatus.attention }}</strong></div></div></div>
      </section>

      <div class="dashboard-lower dashboard-utilities">
        <section class="dashboard-section">
          <h2 class="section-heading">Quick actions</h2>
          <CustomerActionGrid v-if="auth.isCustomer" />
          <div v-else class="quick-actions">
            <q-btn
              v-for="action in quickActions"
              :key="action.label"
              outline
              no-caps
              :icon="action.icon"
              :label="action.label"
              :to="action.to"
              class="quick-action"
            />
          </div>
        </section>
        <section class="dashboard-section">
          <h2 class="section-heading">Session</h2>
          <div class="dashboard-note">
            <q-icon name="verified_user" size="18px" />
            <span>Signed in as {{ auth.roleName || 'user' }}. Activity is recorded in the audit log.</span>
          </div>
        </section>
      </div>
      <div v-if="auth.isCustomer" class="dashboard-lower">
        <section class="dashboard-section"><div class="row justify-between items-center q-mb-md"><h2 class="section-heading q-mb-none">Recent activity</h2><q-btn flat color="primary" label="View all" to="/my-transactions" /></div><div v-for="item in activity.slice(0, 5)" :key="item.id" class="activity-row"><div class="activity-icon" :class="{ incoming: item.direction === 'CREDIT' }"><q-icon :name="item.direction === 'CREDIT' ? 'south_west' : 'north_east'" size="21px" /></div><div class="activity-detail"><strong>{{ item.transaction_type.replaceAll('_', ' ') }}</strong><small>{{ new Date(item.transaction_date).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' }) }} · {{ item.status }}</small></div><strong :class="item.direction === 'CREDIT' ? 'text-positive' : ''">{{ item.direction === 'CREDIT' ? '+' : '−' }}{{ formatCurrency(item.amount) }}</strong></div><p v-if="!activity.length" class="page-subtitle">Your transactions will appear here when you start banking.</p></section>
        <section class="dashboard-section"><div class="eyebrow">MONEY IN / MONEY OUT</div><h2 class="section-heading">Your cash flow</h2><div class="cash-flow-chart"><div class="cash-flow-pie" :style="cashFlowChartStyle" role="img" :aria-label="cashFlowChartLabel"><div><strong>{{ cashFlowTotal ? `${moneyInPercent}%` : '—' }}</strong><span>money in</span></div></div><div class="cash-flow-legend"><div v-for="flow in cashFlow" :key="flow.label"><span class="cash-flow-key" :class="flow.className" /><span>{{ flow.label }}</span><strong>{{ formatCurrency(flow.amount) }}</strong></div></div></div><p class="page-subtitle">Based on your recorded account activity.</p></section>
      </div>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api'
import { preferences } from '@/utils/preferences'
import { useAuthStore } from '@/stores/auth-store'
import BankLogo from '@/components/BankLogo.vue'
import CustomerActionGrid from '@/components/CustomerActionGrid.vue'

const auth = useAuthStore()
const loading = ref(true)
const cards = ref([])
const customerAccounts = ref([])
const activity = ref([])
const accountStatus = ref({ active: 0, attention: 0 })
const hidden = ref(preferences(auth.userId).hideBalance)
const balance = computed(() => customerAccounts.value.reduce((sum, item) => sum + Number(item.available_balance), 0))
const cashFlow = computed(() => [{ label: 'Money in', className: 'money-in', amount: activity.value.filter(t => t.direction === 'CREDIT').reduce((n, t) => n + Number(t.amount), 0) }, { label: 'Money out', className: 'money-out', amount: activity.value.filter(t => t.direction === 'DEBIT').reduce((n, t) => n + Number(t.amount), 0) }])
const cashFlowTotal = computed(() => cashFlow.value.reduce((total, flow) => total + flow.amount, 0))
const moneyInPercent = computed(() => cashFlowTotal.value ? Math.round(cashFlow.value[0].amount / cashFlowTotal.value * 100) : 0)
const cashFlowChartStyle = computed(() => ({ background: cashFlowTotal.value ? `conic-gradient(#138a5b 0 ${moneyInPercent.value}%, #b9e5d2 ${moneyInPercent.value}% 100%)` : '#e8eee9' }))
const cashFlowChartLabel = computed(() => cashFlowTotal.value ? `Cash flow: ${moneyInPercent.value}% money in and ${100 - moneyInPercent.value}% money out` : 'No cash flow activity yet')
const accountStatusTotal = computed(() => accountStatus.value.active + accountStatus.value.attention)
const activeAccountPercent = computed(() => accountStatusTotal.value ? Math.round(accountStatus.value.active / accountStatusTotal.value * 100) : 0)
const accountStatusChartStyle = computed(() => ({ background: accountStatusTotal.value ? `conic-gradient(#138a5b 0 ${activeAccountPercent.value}%, #b9e5d2 ${activeAccountPercent.value}% 100%)` : '#e8eee9' }))
const accountStatusChartLabel = computed(() => accountStatusTotal.value ? `Account status: ${accountStatus.value.active} active and ${accountStatus.value.attention} needing attention` : 'No accounts on record')
const errorMessage = ref('')
const today = new Intl.DateTimeFormat('en-PH', { dateStyle: 'full' }).format(new Date())
const displayName = computed(() => auth.fullName || auth.username || 'there')
const dashboardSubtitle = computed(() => auth.isCustomer
  ? 'Balances, payments, and recent activity in one clear view.'
  : auth.isAdmin
    ? 'Manage access, products, controls, and the bank audit trail.'
    : 'Serve customers, process transactions, and review pending work.')
const mobilePrimaryActions = [
  { label: 'Send', icon: 'send', to: '/customer/transfers' },
  { label: 'Receive', icon: 'south', to: '/my-account?receive=1' },
  { label: 'Scan', icon: 'qr_code_scanner', to: '/customer/transfers?scan=1' },
  { label: 'Pay Bills', icon: 'receipt_long', to: '/customer/bill-payments' },
]
const quickActions = computed(() => {
  if (auth.isAdmin) {
    return [
      { label: 'Manage users', icon: 'manage_accounts', to: '/admin/users' },
      { label: 'Review audit trail', icon: 'history', to: '/admin/audit-logs' },
      { label: 'Configure products', icon: 'tune', to: '/admin/account-types' },
      { label: 'Review requests', icon: 'inbox', to: '/requests' },
    ]
  }
  if (auth.isStaff) {
    return [
      { label: 'Open account', icon: 'person_add', to: '/accounts' },
      { label: 'Record deposit', icon: 'add_card', to: '/deposits' },
      { label: 'Record withdrawal', icon: 'payments', to: '/withdrawals' },
      { label: 'Transfer funds', icon: 'swap_horiz', to: '/transfers' },
    ]
  }
  return []
})

function formatCurrency (value) {
  return `₱ ${Number(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

async function loadAdminCards () {
  const [users, accounts, auditLogs] = await Promise.all([
    api.get('/users/'),
    api.get('/accounts/'),
    api.get('/audit-logs/'),
  ])
  const totalBalance = accounts.data.reduce((sum, account) => sum + Number(account.available_balance), 0)
  accountStatus.value = { active: accounts.data.filter(account => account.status === 'ACTIVE').length, attention: accounts.data.filter(account => account.status !== 'ACTIVE').length }
  cards.value = [
    { label: 'Customers and staff', value: users.data.length, context: 'All registered users with bank access', icon: 'people', to: '/admin/users' },
    { label: 'Bank accounts', value: accounts.data.length, context: 'All customer accounts on record', icon: 'account_balance_wallet', to: '/accounts' },
    { label: 'Available funds', value: formatCurrency(totalBalance), context: 'Combined available balance across accounts', icon: 'payments', to: '/accounts' },
    { label: 'Audit events', value: auditLogs.data.length, context: 'Recorded security and account activity', icon: 'history', to: '/admin/audit-logs' },
  ]
}

async function loadStaffCards () {
  const [accounts, deposits, withdrawals, interbank] = await Promise.all([
    api.get('/accounts/'),
    api.get('/deposits/'),
    api.get('/withdrawals/'),
    api.get('/interbank-transfers/'),
  ])
  const pending = interbank.data.filter((item) => item.status === 'PROCESSING').length
  const totalBalance = accounts.data.reduce((sum, account) => sum + Number(account.available_balance), 0)
  accountStatus.value = { active: accounts.data.filter(account => account.status === 'ACTIVE').length, attention: accounts.data.filter(account => account.status !== 'ACTIVE').length }
  cards.value = [
    { label: 'Bank accounts', value: accounts.data.length, context: 'All customer accounts staff can service', icon: 'account_balance_wallet', to: '/accounts' },
    { label: 'Available funds', value: formatCurrency(totalBalance), context: 'Combined available balance across accounts', icon: 'payments', to: '/accounts' },
    { label: 'Deposits', value: deposits.data.length, context: 'Deposit transactions recorded to date', icon: 'add_card', to: '/deposits' },
    { label: 'Withdrawals', value: withdrawals.data.length, context: 'Withdrawal transactions recorded to date', icon: 'payments', to: '/withdrawals' },
    { label: 'Awaiting settlement', value: pending, context: 'Interbank transfers currently processing', icon: 'sync_alt', to: '/interbank-transfers' },
  ]
}

async function loadCustomerCards () {
  const [{ data: mine }, { data: billPayments }, { data: transactions }] = await Promise.all([
    api.get('/customer/accounts/'),
    api.get('/customer/bill-payments/'),
    api.get('/customer/transactions/'),
  ])
  customerAccounts.value = mine
  activity.value = transactions
  const totalBalance = mine.reduce((sum, account) => sum + Number(account.available_balance), 0)
  cards.value = [
    { label: 'My accounts', value: mine.length, context: 'Accounts connected to your profile', icon: 'account_balance_wallet', to: '/my-account' },
    { label: 'Available to use', value: formatCurrency(totalBalance), context: 'Combined spendable balance right now', icon: 'payments', to: '/my-account' },
    { label: 'Bill payments', value: billPayments.length, context: 'Payments recorded in your history', icon: 'receipt_long', to: '/customer/bill-payments' },
    { label: 'Transactions', value: transactions.length, context: 'Money movements recorded to date', icon: 'history', to: '/my-transactions' },
  ]
}

onMounted(async () => {
  try {
    if (auth.isAdmin) await loadAdminCards()
    else if (auth.isStaff) await loadStaffCards()
    else if (auth.isCustomer) await loadCustomerCards()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Workspace data could not be loaded. Check the API connection and retry.'
  } finally {
    loading.value = false
  }
})
</script>
