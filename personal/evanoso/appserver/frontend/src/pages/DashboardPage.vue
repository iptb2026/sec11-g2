<template>
  <q-page class="dashboard-page" :class="{ 'customer-dashboard': auth.isCustomer }">
    <div class="page-heading">
      <div>
        <div class="eyebrow">{{ auth.isCustomer ? 'YOUR EVERYDAY, SIMPLIFIED' : 'BEMBANK WORKSPACE' }}</div>
        <h1 class="page-title">Welcome back, {{ displayName }} <span class="greeting-dot">✦</span></h1>
        <p class="page-subtitle">{{ auth.isCustomer ? 'A clear view of your money. A little more peace of mind.' : 'Everything you need to keep banking moving.' }}</p>
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
      <div v-if="auth.isCustomer" class="overview-hero">
        <section class="balance-hero"><div class="row items-center justify-between"><span>Total available balance</span><q-btn flat round size="sm" :icon="hidden ? 'visibility_off' : 'visibility'" :aria-label="hidden ? 'Show balance' : 'Hide balance'" @click="hidden = !hidden" /></div><div class="hero-amount">{{ hidden ? '••••••' : formatCurrency(balance) }}</div><div class="balance-caption">Across {{ customerAccounts.length }} Bembank accounts</div><div class="hero-bottom"><span><span class="status-dot" /> Your everyday essentials, connected</span><BankLogo /></div></section>
        <section class="customer-panel move-panel"><div class="eyebrow">MAKE YOUR NEXT MOVE</div><h2>Small steps. <br>Big possibilities.</h2><p>Give your next adventure a savings goal.</p><q-btn flat no-caps label="Explore savings goals" icon-right="north_east" to="/customer/savings" color="primary" /></section>
      </div>
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
        <section class="dashboard-section"><div class="eyebrow">MONEY IN / MONEY OUT</div><h2 class="section-heading">Your cash flow</h2><div v-for="flow in cashFlow" :key="flow.label" class="cash-flow"><div class="row justify-between q-mb-sm"><span>{{ flow.label }}</span><strong>{{ formatCurrency(flow.amount) }}</strong></div><q-linear-progress rounded size="9px" :value="flow.amount / Math.max(...cashFlow.map(f => f.amount), 1)" :color="flow.color" /></div><p class="page-subtitle">Based on your recorded account activity.</p></section>
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
const hidden = ref(preferences(auth.userId).hideBalance)
const balance = computed(() => customerAccounts.value.reduce((sum, item) => sum + Number(item.available_balance), 0))
const cashFlow = computed(() => [{ label: 'Money in', color: 'positive', amount: activity.value.filter(t => t.direction === 'CREDIT').reduce((n, t) => n + Number(t.amount), 0) }, { label: 'Money out', color: 'primary', amount: activity.value.filter(t => t.direction === 'DEBIT').reduce((n, t) => n + Number(t.amount), 0) }])
const errorMessage = ref('')
const today = new Intl.DateTimeFormat('en-PH', { dateStyle: 'full' }).format(new Date())
const displayName = computed(() => auth.fullName || auth.username || 'there')
const mobilePrimaryActions = [
  { label: 'Send', icon: 'send', to: '/customer/transfers' },
  { label: 'Receive', icon: 'south', to: '/my-account?receive=1' },
  { label: 'Scan', icon: 'qr_code_scanner', to: '/customer/transfers?scan=1' },
  { label: 'Pay Bills', icon: 'receipt_long', to: '/customer/bill-payments' },
]
const quickActions = computed(() => {
  if (auth.isAdmin || auth.isStaff) {
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
  const [roles, users, accounts, banks, auditLogs] = await Promise.all([
    api.get('/roles/'),
    api.get('/users/'),
    api.get('/accounts/'),
    api.get('/banks/'),
    api.get('/audit-logs/'),
  ])
  const totalBalance = accounts.data.reduce((sum, account) => sum + Number(account.available_balance), 0)
  cards.value = [
    { label: 'Customers and staff', value: users.data.length, icon: 'people', to: '/admin/users' },
    { label: 'Open accounts', value: accounts.data.length, icon: 'account_balance_wallet', to: '/accounts' },
    { label: 'Available funds', value: formatCurrency(totalBalance), icon: 'payments', to: '/accounts' },
    { label: 'Audit events', value: auditLogs.data.length, icon: 'history', to: '/admin/audit-logs' },
    { label: 'Access roles', value: roles.data.length, icon: 'admin_panel_settings', to: '/admin/roles' },
    { label: 'Registered banks', value: banks.data.length, icon: 'account_balance', to: '/admin/banks' },
  ]
}

async function loadStaffCards () {
  const [accounts, deposits, withdrawals, transfers, interbank] = await Promise.all([
    api.get('/accounts/'),
    api.get('/deposits/'),
    api.get('/withdrawals/'),
    api.get('/transfers/'),
    api.get('/interbank-transfers/'),
  ])
  const pending = interbank.data.filter((item) => item.status === 'PROCESSING').length
  const totalBalance = accounts.data.reduce((sum, account) => sum + Number(account.available_balance), 0)
  cards.value = [
    { label: 'Open accounts', value: accounts.data.length, icon: 'account_balance_wallet', to: '/accounts' },
    { label: 'Available funds', value: formatCurrency(totalBalance), icon: 'payments', to: '/accounts' },
    { label: 'Deposits', value: deposits.data.length, icon: 'add_card', to: '/deposits' },
    { label: 'Withdrawals', value: withdrawals.data.length, icon: 'payments', to: '/withdrawals' },
    { label: 'Internal transfers', value: transfers.data.length, icon: 'swap_horiz', to: '/transfers' },
    { label: 'Awaiting settlement', value: pending, icon: 'sync_alt', to: '/interbank-transfers' },
  ]
}

async function loadCustomerCards () {
  const [{ data: mine }, { data: investments }, { data: billPayments }, { data: transactions }] = await Promise.all([
    api.get('/customer/accounts/'),
    api.get('/customer/investments/'),
    api.get('/customer/bill-payments/'),
    api.get('/customer/transactions/'),
  ])
  customerAccounts.value = mine
  activity.value = transactions
  const totalBalance = mine.reduce((sum, account) => sum + Number(account.available_balance), 0)
  const activeInvestments = investments.filter((item) => item.status === 'ACTIVE')
  const investmentTotal = activeInvestments.reduce((sum, item) => sum + Number(item.amount), 0)
  cards.value = [
    { label: 'My accounts', value: mine.length, icon: 'account_balance_wallet', to: '/my-account' },
    { label: 'Total available balance', value: formatCurrency(totalBalance), icon: 'payments', to: '/my-account' },
    { label: 'Allocated investments', value: formatCurrency(investmentTotal), icon: 'trending_up', to: '/customer/investments' },
    { label: 'Bill payments', value: billPayments.length, icon: 'receipt_long', to: '/customer/bill-payments' },
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
