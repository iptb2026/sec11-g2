<template>
  <q-page class="dashboard-page q-pa-md q-pa-lg-xl">
    <div class="dashboard-shell">
      <header class="page-header">
        <div>
          <p class="eyebrow">MARQUISO BANKING</p>
          <h1>Operations overview</h1>
          <p class="subtitle">Live status from your FastAPI service.</p>
        </div>
        <div class="header-actions">
          <q-badge v-if="authStore.roleName" color="secondary" :label="authStore.roleName" />
          <q-btn
            class="refresh-button"
            color="primary"
            unelevated
            no-caps
            :loading="loading"
            icon="refresh"
            label="Refresh"
            @click="fetchDashboard"
          />
        </div>
      </header>

      <section class="access-panel">
        <div>
          <p class="panel-label">CURRENT ACCESS</p>
          <h2>{{ authStore.fullName || authStore.username || 'Guest user' }}</h2>
          <p class="panel-copy">{{ accessSummary }}</p>
        </div>
        <q-icon :name="accessIcon" size="38px" />
      </section>

      <section class="status-panel" :class="{ 'status-panel--error': error }">
        <div class="status-icon" :class="error ? 'status-icon--error' : 'status-icon--ok'">
          <q-icon :name="error ? 'cloud_off' : 'cloud_done'" size="26px" />
        </div>
        <div>
          <p class="panel-label">API CONNECTION</p>
          <h2>{{ error ? 'Connection unavailable' : (health?.status || 'Checking service...') }}</h2>
          <p class="panel-copy">{{ error || 'Connected to the local FastAPI service' }}</p>
        </div>
      </section>

      <section class="metrics-grid">
        <article class="metric-card">
          <q-icon name="account_balance" size="24px" />
          <span class="metric-label">Service</span>
          <strong>{{ health?.app || '—' }}</strong>
        </article>
        <article class="metric-card">
          <q-icon name="account_balance_wallet" size="24px" />
          <span class="metric-label">Banks available</span>
          <strong>{{ banks.length }}</strong>
        </article>
        <article class="metric-card">
          <q-icon name="verified" size="24px" />
          <span class="metric-label">API status</span>
          <strong>{{ loading ? 'Loading' : error ? 'Offline' : 'Online' }}</strong>
        </article>
      </section>

      <section class="balance-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ authStore.isCustomer ? 'MY MONEY' : 'OPERATIONS' }}</p>
            <h2>{{ authStore.isCustomer ? 'My balance' : 'Managed account balances' }}</h2>
          </div>
          <strong class="balance-total">PHP {{ totalBalance }}</strong>
        </div>
        <q-list v-if="visibleAccounts.length" class="balance-list">
          <q-item v-for="account in visibleAccounts" :key="account.id">
            <q-item-section avatar><q-icon name="account_balance_wallet" color="positive" size="24px" /></q-item-section>
            <q-item-section>
              <q-item-label>{{ account.account_number }}</q-item-label>
              <q-item-label caption>
                {{ authStore.isCustomer ? authStore.fullName : `Customer #${account.customer_id}` }}
                &middot; {{ accountTypeName(account.account_type_id) }}
              </q-item-label>
              <q-item-label caption>
                {{ account.currency_code }} &middot; {{ account.status }} &middot; Branch {{ account.branch_code || 'Not assigned' }}
                &middot; Opened {{ formatDate(account.opened_at) }}
              </q-item-label>
            </q-item-section>
            <q-item-section side class="balance-values">
              <strong>{{ account.currency_code }} {{ account.available_balance }}</strong>
              <span>Ledger {{ account.ledger_balance }}</span>
            </q-item-section>
          </q-item>
        </q-list>
        <div v-else class="empty-state"><q-icon name="account_balance_wallet" size="32px" /><p>No account balance available.</p></div>
      </section>

      <section v-if="authStore.isCustomer" class="history-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">MY ACTIVITY</p>
            <h2>Transaction history</h2>
          </div>
          <q-badge color="secondary" :label="`${customerTransactions.length} records`" />
        </div>
        <q-list v-if="customerTransactions.length" class="history-list">
          <q-item v-for="transaction in customerTransactions" :key="transaction.key">
            <q-item-section avatar><q-icon :name="transaction.icon" :color="transaction.color" size="24px" /></q-item-section>
            <q-item-section>
              <q-item-label>{{ transaction.label }}</q-item-label>
              <q-item-label caption>{{ transaction.reference }} &middot; Account #{{ transaction.accountId }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <strong :class="`amount-${transaction.direction}`">{{ transaction.direction === 'in' ? '+' : '-' }} PHP {{ transaction.amount }}</strong>
              <span>{{ formatDate(transaction.date) }}</span>
            </q-item-section>
          </q-item>
        </q-list>
        <div v-else class="empty-state"><q-icon name="receipt_long" size="32px" /><p>No transactions yet.</p></div>
      </section>

      <section class="banking-actions">
        <div class="section-heading">
          <div>
            <p class="eyebrow">BANKING OPERATIONS</p>
            <h2>Deposit, withdraw, and transfer</h2>
          </div>
          <q-badge color="secondary" :label="`${visibleAccounts.length} account(s)`" />
        </div>
        <div v-if="visibleAccounts.length" class="action-grid">
          <q-card class="action-card">
            <q-card-section>
              <q-icon name="add_card" size="26px" color="positive" />
              <h3>Deposit</h3>
              <p>Add funds to an active account.</p>
              <q-select v-model="depositForm.account_id" outlined emit-value map-options :options="accountOptions" label="Account" />
              <q-input v-model.number="depositForm.amount" outlined type="number" min="0.01" step="0.01" label="Amount" prefix="PHP" />
              <q-btn color="primary" unelevated no-caps icon="add" label="Submit deposit" :disable="!canDeposit" :loading="actionLoading === 'deposit'" @click="submitDeposit" />
            </q-card-section>
          </q-card>
          <q-card class="action-card">
            <q-card-section>
              <q-icon name="payments" size="26px" color="warning" />
              <h3>Withdraw</h3>
              <p>Withdraw available funds from an account.</p>
              <q-select v-model="withdrawForm.account_id" outlined emit-value map-options :options="accountOptions" label="Account" />
              <q-input v-model.number="withdrawForm.amount" outlined type="number" min="0.01" step="0.01" label="Amount" prefix="PHP" />
              <q-btn color="primary" unelevated no-caps icon="remove" label="Submit withdrawal" :disable="!canWithdraw" :loading="actionLoading === 'withdraw'" @click="submitWithdrawal" />
            </q-card-section>
          </q-card>
          <q-card class="action-card action-card--wide">
            <q-card-section>
              <q-icon name="swap_horiz" size="26px" color="info" />
              <h3>Transfer</h3>
              <p>Move funds between two active accounts.</p>
              <div class="transfer-fields">
                <q-select v-model="transferForm.source_account_id" outlined emit-value map-options :options="accountOptions" label="From account" />
                <q-select v-if="!authStore.isCustomer" v-model="transferForm.destination_account_id" outlined emit-value map-options :options="accountOptions" label="To account" />
                <q-input v-else v-model.number="transferForm.destination_account_id" outlined type="number" min="1" label="Recipient account ID" />
              </div>
              <q-input v-model.number="transferForm.amount" outlined type="number" min="0.01" step="0.01" label="Amount" prefix="PHP" />
              <q-btn color="primary" unelevated no-caps icon="send" label="Submit transfer" :disable="!canTransfer" :loading="actionLoading === 'transfer'" @click="submitTransfer" />
            </q-card-section>
          </q-card>
        </div>
        <div v-else class="empty-state">
          <q-icon name="account_balance_wallet" size="32px" />
          <p>No bank account is linked to this user yet.</p>
          <q-btn v-if="authStore.isCustomer" color="primary" unelevated no-caps icon="add_card" label="Open savings account" :loading="actionLoading === 'account'" @click="openCustomerAccount" />
        </div>
        <q-banner v-if="actionMessage" rounded class="action-message" :class="{ 'action-message--error': actionError }">
          <template #avatar><q-icon :name="actionError ? 'error_outline' : 'task_alt'" /></template>
          {{ actionMessage }}
        </q-banner>
      </section>

      <section v-if="!authStore.isCustomer" class="banks-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">REFERENCE DATA</p>
            <h2>Connected banks</h2>
          </div>
          <q-badge color="secondary" :label="`${banks.length} records`" />
        </div>
        <q-list v-if="banks.length" class="bank-list">
          <q-item v-for="bank in banks" :key="bank.id" class="bank-item">
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" icon="account_balance" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ bank.bank_name || bank.name || `Bank #${bank.id}` }}</q-item-label>
              <q-item-label caption>{{ bank.bank_code || 'Registered institution' }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
        <div v-else class="empty-state">
          <q-icon name="account_balance" size="32px" />
          <p>{{ loading ? 'Loading bank records...' : 'No bank records returned yet.' }}</p>
        </div>
      </section>

      <section v-if="!authStore.isCustomer" class="capabilities-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">ROLE CAPABILITIES</p>
            <h2>Available operations</h2>
          </div>
        </div>
        <div class="capabilities-grid">
          <article v-for="capability in capabilities" :key="capability.title" class="capability-card">
            <q-icon :name="capability.icon" size="24px" />
            <div>
              <h3>{{ capability.title }}</h3>
              <p>{{ capability.description }}</p>
            </div>
            <q-badge :color="capability.restricted ? 'grey-6' : 'positive'" :label="capability.restricted ? 'Restricted' : 'Available'" />
          </article>
        </div>
      </section>

      <section v-if="!authStore.isCustomer" class="role-walkthrough">
        <div class="section-heading">
          <div>
            <p class="eyebrow">ACCESS WALKTHROUGH</p>
            <h2>Compare account access</h2>
          </div>
          <span class="walkthrough-note">Your current role is highlighted</span>
        </div>
        <div class="role-grid">
          <article v-for="role in visibleRoleWalkthrough" :key="role.code" class="role-card" :class="{ 'role-card--current': authStore.roleCode === role.code }">
            <div class="role-card-heading">
              <q-icon :name="role.icon" size="28px" />
              <q-badge v-if="authStore.roleCode === role.code" color="positive" label="Current role" />
            </div>
            <p class="role-code">{{ role.code }}</p>
            <h3>{{ role.name }}</h3>
            <p>{{ role.description }}</p>
            <div class="role-operation"><q-icon name="play_circle" size="18px" /><span>{{ role.operation }}</span></div>
            <div class="role-access-list"><span v-for="item in role.access" :key="item">{{ item }}</span></div>
          </article>
        </div>
      </section>

      <section class="operation-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">FRONTEND SIMULATION</p>
            <h2>Run a role operation</h2>
          </div>
        </div>
        <div class="operation-panel">
          <div>
            <p class="panel-label">{{ operationLabel }}</p>
            <p class="panel-copy">{{ operationDescription }}</p>
            <q-banner v-if="operationResult" rounded class="operation-result">
              <template #avatar><q-icon name="task_alt" /></template>
              {{ operationResult }}
            </q-banner>
          </div>
          <q-btn
            color="primary"
            unelevated
            no-caps
            icon="play_arrow"
            :label="operationButton"
            :loading="operationLoading"
            @click="runRoleOperation"
          />
        </div>
        <q-list v-if="authStore.isAdmin && adminUsers.length" class="admin-directory">
          <q-item v-for="user in adminUsers" :key="user.id">
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" icon="person" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ user.username }}</q-item-label>
              <q-item-label caption>{{ user.first_name }} {{ user.last_name }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-badge color="secondary" :label="user.role_id === 1 ? 'ADMIN' : `Role ${user.role_id}`" />
            </q-item-section>
          </q-item>
        </q-list>
      </section>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const authStore = useAuthStore()
const health = ref(null)
const banks = ref([])
const loading = ref(false)
const error = ref('')
const accounts = ref([])
const deposits = ref([])
const withdrawals = ref([])
const transfers = ref([])
const actionLoading = ref('')
const actionMessage = ref('')
const actionError = ref(false)
const depositForm = ref({ account_id: null, amount: null })
const withdrawForm = ref({ account_id: null, amount: null })
const transferForm = ref({ source_account_id: null, destination_account_id: null, amount: null })

const canDeposit = computed(() => Boolean(depositForm.value.account_id && Number(depositForm.value.amount) > 0))
const canWithdraw = computed(() => Boolean(withdrawForm.value.account_id && Number(withdrawForm.value.amount) > 0))
const canTransfer = computed(() => Boolean(
  transferForm.value.source_account_id &&
  transferForm.value.destination_account_id &&
  Number(transferForm.value.amount) > 0 &&
  transferForm.value.source_account_id !== transferForm.value.destination_account_id,
))

const visibleAccounts = computed(() => authStore.isCustomer
  ? accounts.value.filter((account) => account.customer_id === authStore.userId)
  : accounts.value)

const accountOptions = computed(() => visibleAccounts.value.map((account) => ({
  label: `${account.account_number} - PHP ${account.available_balance}`,
  value: account.id,
})))

const totalBalance = computed(() => visibleAccounts.value
  .reduce((total, account) => total + Number(account.available_balance || 0), 0)
  .toFixed(2))

const customerTransactions = computed(() => [
  ...deposits.value.map((item) => ({ key: `deposit-${item.id}`, label: 'Deposit', reference: item.reference_number, accountId: item.account_id, amount: item.amount, date: item.transaction_date, icon: 'add_circle', color: 'positive', direction: 'in' })),
  ...withdrawals.value.map((item) => ({ key: `withdrawal-${item.id}`, label: 'Withdrawal', reference: item.reference_number, accountId: item.account_id, amount: item.amount, date: item.transaction_date, icon: 'remove_circle', color: 'warning', direction: 'out' })),
  ...transfers.value.map((item) => ({ key: `transfer-${item.id}`, label: 'Transfer', reference: item.transfer_reference, accountId: item.source_account_id, amount: item.amount, date: item.created_at, icon: 'swap_horiz', color: 'info', direction: 'out' })),
].sort((first, second) => new Date(second.date) - new Date(first.date)))

function accountTypeName (accountTypeId) {
  return accountTypeId === 1 ? 'Savings Account' : `Account type #${accountTypeId}`
}

function formatDate (date) {
  return date ? new Date(date).toLocaleDateString() : 'Not available'
}
const operationLoading = ref(false)
const operationResult = ref('')
const adminUsers = ref([])

const accessSummary = computed(() => {
  if (authStore.isAdmin) return 'Full system access, including users, roles, and bank configuration.'
  if (authStore.isStaff) return 'Operational access for deposits, withdrawals, transfers, and customer service.'
  if (authStore.roleCode === 'MANAGER') return 'Branch oversight access for operational and financial activity.'
  if (authStore.isCustomer) return 'Personal banking access for your own accounts and transactions.'
  return 'Sign in to see the operations available for your role.'
})

const accessIcon = computed(() => {
  if (authStore.isAdmin) return 'admin_panel_settings'
  if (authStore.isCustomer) return 'person'
  return 'badge'
})

const capabilities = computed(() => {
  const role = authStore.roleCode
  const allCapabilities = [
    { title: 'User and role management', description: 'Create users and assign banking roles.', icon: 'manage_accounts', restricted: role !== 'ADMIN' },
    { title: 'Transaction operations', description: 'Process deposits, withdrawals, and transfers.', icon: 'swap_horiz', restricted: !['ADMIN', 'STAFF', 'MANAGER'].includes(role) },
    { title: 'Personal account access', description: 'View your own account and transaction information.', icon: 'account_balance_wallet', restricted: !role },
    { title: 'Bank configuration', description: 'Manage banks, account types, fees, and policies.', icon: 'settings', restricted: !['ADMIN', 'MANAGER'].includes(role) },
  ]
  return authStore.isAdmin ? allCapabilities : allCapabilities.filter((capability) => capability.title !== 'User and role management')
})

const roleWalkthrough = [
  { code: 'ADMIN', name: 'Administrator', icon: 'admin_panel_settings', description: 'Controls identity, roles, configuration, and all operational data.', operation: 'Load the complete user directory', access: ['Users and roles', 'Bank configuration', 'All transactions'] },
  { code: 'STAFF', name: 'Staff', icon: 'support_agent', description: 'Handles day-to-day customer and transaction operations.', operation: 'Load deposit operations', access: ['Deposits and withdrawals', 'Customer service', 'Transfers'] },
  { code: 'MANAGER', name: 'Manager', icon: 'business_center', description: 'Oversees branch activity and operational performance.', operation: 'Load branch transfers', access: ['Branch operations', 'Financial activity', 'Bank policies'] },
  { code: 'CUSTOMER', name: 'Customer', icon: 'person', description: 'Uses personal banking services and views their own information.', operation: 'Load my profile', access: ['Own profile', 'Own accounts', 'Own transactions'] },
]

const visibleRoleWalkthrough = computed(() => authStore.isAdmin
  ? roleWalkthrough
  : roleWalkthrough.filter((role) => role.code !== 'ADMIN'))

const operationLabel = computed(() => {
  if (authStore.isAdmin) return 'ADMIN OPERATION'
  if (authStore.isStaff) return 'STAFF OPERATION'
  if (authStore.roleCode === 'MANAGER') return 'MANAGER OPERATION'
  return 'CUSTOMER OPERATION'
})

const operationButton = computed(() => {
  if (authStore.isAdmin) return 'Load user directory'
  if (authStore.isStaff) return 'Load deposits'
  if (authStore.roleCode === 'MANAGER') return 'Load transfers'
  return 'Load my profile'
})

const operationDescription = computed(() => {
  if (authStore.isAdmin) return 'Admin can inspect the complete user directory.'
  if (authStore.isStaff) return 'Staff can inspect deposit operations for customer service.'
  if (authStore.roleCode === 'MANAGER') return 'Managers can inspect branch transfer activity.'
  return 'Customers can retrieve their own profile information.'
})

async function fetchDashboard () {
  loading.value = true
  error.value = ''

  try {
    const [healthResponse, accountsResponse] = await Promise.all([api.get('/'), api.get('/accounts/')])
    const banksResponse = authStore.isAdmin || authStore.roleCode === 'MANAGER' ? await api.get('/banks/') : null
    health.value = healthResponse.data
    banks.value = Array.isArray(banksResponse?.data) ? banksResponse.data : []
    accounts.value = Array.isArray(accountsResponse.data) ? accountsResponse.data : []
    if (authStore.isCustomer) {
      const [depositsResponse, withdrawalsResponse, transfersResponse] = await Promise.all([
        api.get('/deposits/'),
        api.get('/withdrawals/'),
        api.get('/transfers/'),
      ])
      deposits.value = depositsResponse.data
      withdrawals.value = withdrawalsResponse.data
      transfers.value = transfersResponse.data
    }
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not reach the banking API.'
  } finally {
    loading.value = false
  }
}

function makeReference (prefix) {
  return `${prefix}-${Date.now()}`
}

async function submitDeposit () {
  await submitAction('deposit', '/deposits/', {
    account_id: depositForm.value.account_id,
    reference_number: makeReference('DEP'),
    amount: depositForm.value.amount,
    deposit_channel: 'ONLINE',
    deposited_by_user_id: authStore.userId,
  })
}

async function submitWithdrawal () {
  await submitAction('withdraw', '/withdrawals/', {
    account_id: withdrawForm.value.account_id,
    reference_number: makeReference('WDR'),
    amount: withdrawForm.value.amount,
    withdrawal_channel: 'ONLINE',
    approved_by_user_id: authStore.isCustomer ? null : authStore.userId,
  })
}

async function submitTransfer () {
  await submitAction('transfer', '/transfers/', {
    source_account_id: transferForm.value.source_account_id,
    destination_account_id: transferForm.value.destination_account_id,
    transfer_reference: makeReference('TRF'),
    amount: transferForm.value.amount,
    transfer_type: 'INTERNAL',
  })
}

async function openCustomerAccount () {
  actionLoading.value = 'account'
  actionMessage.value = ''
  actionError.value = false

  try {
    await api.post('/accounts/', {
      account_number: `SAV-${authStore.userId}-${Date.now()}`,
      customer_id: authStore.userId,
      account_type_id: 1,
      currency_code: 'PHP',
    })
    actionMessage.value = 'Savings account opened successfully. You can now deposit funds.'
    await fetchDashboard()
  } catch (requestError) {
    actionError.value = true
    actionMessage.value = requestError.response?.data?.detail || 'Unable to open the savings account.'
  } finally {
    actionLoading.value = ''
  }
}

async function submitAction (action, endpoint, payload) {
  actionLoading.value = action
  actionMessage.value = ''
  actionError.value = false

  try {
    await api.post(endpoint, payload)
    actionMessage.value = `${action[0].toUpperCase()}${action.slice(1)} completed successfully.`
    await fetchDashboard()
  } catch (requestError) {
    actionError.value = true
    actionMessage.value = requestError.response?.data?.detail || `Unable to complete ${action}.`
  } finally {
    actionLoading.value = ''
  }
}

async function runRoleOperation () {
  operationLoading.value = true
  operationResult.value = ''

  try {
    if (authStore.isAdmin) {
      const { data } = await api.get('/users/')
      adminUsers.value = data
      operationResult.value = `Admin operation complete: ${data.length} user record(s) loaded.`
    } else if (authStore.isStaff) {
      const { data } = await api.get('/deposits/')
      operationResult.value = `Staff operation complete: ${data.length} deposit record(s) loaded.`
    } else if (authStore.roleCode === 'MANAGER') {
      const { data } = await api.get('/transfers/')
      operationResult.value = `Manager operation complete: ${data.length} transfer record(s) loaded.`
    } else {
      const { data } = await api.get(`/users/${authStore.userId}`)
      operationResult.value = `Customer operation complete: profile loaded for ${data.username}.`
    }
  } catch (requestError) {
    operationResult.value = requestError.response?.data?.detail || 'This operation was rejected by the API.'
  } finally {
    operationLoading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<style scoped>
.dashboard-page {
  background: #f4f7f6;
  color: #182827;
}

.dashboard-shell {
  max-width: 1160px;
  margin: 0 auto;
}

.page-header,
.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}
.header-actions { display: flex; align-items: center; gap: 14px; }

.page-header { padding: 42px 0 30px; }
.eyebrow, .panel-label, .metric-label {
  margin: 0 0 8px;
  color: #53746d;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.6px;
}
h1, h2, p { margin-top: 0; }
h1 { margin-bottom: 8px; font-size: clamp(2rem, 4vw, 3.25rem); line-height: 1; font-weight: 800; }
h2 { margin-bottom: 0; font-size: 1.45rem; font-weight: 750; }
.subtitle { margin-bottom: 0; color: #6b7c78; font-size: 1rem; }
.refresh-button { min-height: 44px; border-radius: 8px; }
.status-panel {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 24px;
  border: 1px solid #cfe3dc;
  border-radius: 12px;
  background: #e8f4ef;
}
.status-panel--error { border-color: #ebcaca; background: #fff0ef; }
.status-icon { display: grid; place-items: center; width: 52px; height: 52px; border-radius: 50%; }
.status-icon--ok { color: #176653; background: #c9e7db; }
.status-icon--error { color: #a53737; background: #f3cccc; }
.panel-label { margin-bottom: 5px; }
.status-panel h2 { margin-bottom: 4px; }
.panel-copy { margin-bottom: 0; color: #60736d; }
.access-panel { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 18px; padding: 22px 24px; border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.access-panel > .q-icon { color: #19866d; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 18px 0 42px; }
.metric-card { display: grid; gap: 10px; padding: 22px; border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.metric-card > .q-icon { color: #19866d; }
.metric-label { margin: 0; color: #74847f; }
.metric-card strong { overflow-wrap: anywhere; font-size: 1.12rem; }
.balance-section { padding-bottom: 42px; }
.balance-total { color: #176653; font-size: 1.65rem; }
.balance-list { border: 1px solid #cfe3dc; border-radius: 10px; background: #fff; }
.balance-list .q-item + .q-item { border-top: 1px solid #edf2f0; }
.balance-values { align-items: flex-end; gap: 4px; }
.balance-values span { color: #71817d; font-size: .75rem; }
.history-section { padding-bottom: 42px; }
.history-list { border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.history-list .q-item + .q-item { border-top: 1px solid #edf2f0; }
.history-list .q-item-section[side] { align-items: flex-end; gap: 4px; }
.history-list .q-item-section[side] span { color: #71817d; font-size: .75rem; }
.amount-in { color: #176653; }
.amount-out { color: #9e3737; }
.banking-actions { padding-bottom: 42px; }
.action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.action-card { border: 1px solid #dce7e3; border-radius: 10px; box-shadow: none; }
.action-card--wide { grid-column: 1 / -1; }
.action-card h3 { margin: 12px 0 5px; font-size: 1.1rem; }
.action-card p { margin: 0 0 16px; color: #71817d; font-size: .88rem; }
.action-card .q-select, .action-card .q-input { margin-bottom: 12px; }
.transfer-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.action-message { margin-top: 14px; color: #176653; background: #d7eee5; }
.action-message--error { color: #9e3737; background: #fff0ef; }
.banks-section { padding-bottom: 40px; }
.section-heading { align-items: center; margin-bottom: 16px; }
.bank-list { border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.bank-item + .bank-item { border-top: 1px solid #edf2f0; }
.empty-state { display: grid; place-items: center; gap: 8px; padding: 42px; border: 1px dashed #c6d6d1; color: #71817d; text-align: center; }
.empty-state p { margin: 0; }
.capabilities-section { padding-bottom: 50px; }
.capabilities-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.capability-card { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 14px; padding: 18px; border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.capability-card > .q-icon { color: #19866d; }
.capability-card h3 { margin: 0 0 5px; font-size: 1rem; }
.capability-card p { margin: 0; color: #71817d; font-size: .88rem; }
.role-walkthrough { padding-bottom: 42px; }
.walkthrough-note { color: #71817d; font-size: .85rem; }
.role-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.role-card { display: flex; flex-direction: column; min-height: 290px; padding: 18px; border: 1px solid #dce7e3; border-radius: 10px; background: #fff; }
.role-card--current { border: 2px solid #19866d; box-shadow: 0 8px 24px rgba(25, 134, 109, .12); }
.role-card-heading { display: flex; align-items: center; justify-content: space-between; color: #19866d; }
.role-code { margin: 18px 0 5px; color: #53746d; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; }
.role-card h3 { margin: 0 0 8px; font-size: 1.12rem; }
.role-card > p:not(.role-code) { min-height: 62px; margin: 0; color: #71817d; font-size: .88rem; line-height: 1.5; }
.role-operation { display: flex; align-items: flex-start; gap: 8px; margin: 16px 0; padding: 10px; color: #176653; background: #e8f4ef; font-size: .82rem; font-weight: 700; line-height: 1.35; }
.role-access-list { display: grid; gap: 5px; margin-top: auto; color: #60736d; font-size: .78rem; }
.role-access-list span::before { content: 'ok'; margin-right: 7px; color: #19866d; font-weight: 800; }
.operation-section { padding-bottom: 60px; }
.operation-panel { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 22px 24px; border: 1px solid #cfe3dc; border-radius: 10px; background: #e8f4ef; }
.operation-panel .panel-label { margin-bottom: 5px; }
.operation-result { margin-top: 14px; color: #176653; background: #d7eee5; }
.admin-directory { margin-top: 16px; border: 1px solid #cfe3dc; border-radius: 10px; background: #fff; }
.admin-directory .q-item + .q-item { border-top: 1px solid #edf2f0; }
@media (max-width: 600px) {
  .page-header { align-items: flex-start; flex-direction: column; padding-top: 24px; }
  .header-actions { justify-content: space-between; width: 100%; }
  .refresh-button { width: 100%; }
  .metrics-grid { grid-template-columns: 1fr; margin-bottom: 32px; }
  .action-grid { grid-template-columns: 1fr; }
  .action-card--wide { grid-column: auto; }
  .transfer-fields { grid-template-columns: 1fr; gap: 0; }
  .status-panel { align-items: flex-start; padding: 18px; }
  .capabilities-grid { grid-template-columns: 1fr; }
  .walkthrough-note { display: none; }
  .role-grid { grid-template-columns: 1fr; }
  .role-card { min-height: 0; }
  .operation-panel { align-items: stretch; flex-direction: column; }
}
</style>
