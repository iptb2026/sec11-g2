<template>
  <main class="app-shell">
    <section v-if="!token" class="login-card">
      <div class="brand-mark">B</div><p class="eyebrow">BEMBANK DIGITAL</p><h1>Welcome back</h1><p class="muted">Secure banking, made simple.</p>
      <form @submit.prevent="login">
        <label>Server address<input v-model="serverUrl" type="url" placeholder="http://192.168.x.x:5005" required></label>
        <p class="server-help">Use the laptop Wi-Fi IP and port 5005. This is saved on your phone.</p>
        <label>Username<input v-model="username" autocomplete="username" required></label>
        <label>Password<input v-model="password" type="password" autocomplete="current-password" required></label>
        <p v-if="error" class="error">{{ error }}</p>
        <button :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in securely' }}</button>
      </form>
      <p class="demo-note">Test build · Demo banking app · No real money</p>
    </section>
    <section v-else class="banking">
      <header><div class="header-brand"><span class="mini-mark">B</span><div><strong>BEMBank</strong><small>Digital wallet</small></div></div><button class="link" @click="logout">Log out</button></header>
      <nav><button :class="{ active: page === 'home' }" @click="page = 'home'">⌂<span>Home</span></button><button :class="{ active: page === 'accounts' }" @click="page = 'accounts'">▣<span>Accounts</span></button><button :class="{ active: page === 'transactions' }" @click="page = 'transactions'">≡<span>Activity</span></button><button v-if="user?.username === 'espada'" :class="{ active: page === 'customers' }" @click="page = 'customers'">♙<span>Customers</span></button></nav>
      <p v-if="error" class="error">{{ error }}</p><div v-if="loading">Loading…</div>
      <template v-else-if="page === 'home'"><p class="eyebrow">WELCOME BACK</p><h1>{{ user?.first_name || username }}</h1><section class="balance-card"><div class="card-top"><span>Available balance</span><b>•••</b></div><strong class="balance">{{ money(total) }}</strong><small>{{ accounts[0]?.account_number || 'No active account' }} · BEM SAVINGS</small></section><p class="section-title">Quick actions</p><section class="quick-actions"><button @click="page = 'send'"><b>↗</b><span>Send money</span></button><button @click="page = 'accounts'"><b>▣</b><span>My account</span></button><button @click="page = 'transactions'"><b>◷</b><span>Activity</span></button><button v-if="user?.username === 'espada'" @click="page = 'customers'"><b>♙</b><span>Customers</span></button></section><form v-if="user?.username === 'espada' && accounts.length" class="deposit" @submit.prevent="deposit"><p class="eyebrow">ADMIN CONTROL</p><h2>Add demo money</h2><label>Amount (PHP)<input v-model.number="depositAmount" type="number" min="1" step="0.01" placeholder="0.00" required></label><button :disabled="depositing">{{ depositing ? 'Adding…' : 'Add to account' }}</button></form></template>
      <template v-else-if="page === 'accounts'"><p class="eyebrow">YOUR MONEY</p><h1>Accounts</h1><article v-for="account in accounts" :key="account.id" class="item"><div><small>DEMO SAVINGS</small><strong>{{ account.account_number }}</strong></div><span>{{ money(account.available_balance) }}</span><small class="status">● {{ account.status }}</small></article><p v-if="!accounts.length">No accounts found.</p></template>
      <template v-else-if="page === 'send'"><p class="eyebrow">BEMBANK SEND MONEY · DEMO</p><h1>Send money</h1><form class="deposit" @submit.prevent="transfer"><label>Recipient<select v-model.number="recipientAccountId" required><option :value="null" disabled>Select a demo customer</option><option v-for="recipient in recipients" :key="recipient.id" :value="recipient.id">{{ recipient.customer_name }} · {{ recipient.account_number }}</option></select></label><label>Amount (PHP)<input v-model.number="transferAmount" type="number" min="1" step="0.01" placeholder="0.00" required></label><button :disabled="transferring || !recipients.length">{{ transferring ? 'Sending…' : 'Send money' }}</button></form></template>
      <template v-else-if="page === 'customers'"><p class="eyebrow">ADMIN VIEW · FICTIONAL DATA</p><h1>Customers</h1><article v-for="account in adminAccounts" :key="account.id" class="item"><div><strong>{{ account.customer_name }}</strong><small>{{ account.account_number }}</small></div><span>{{ money(account.available_balance) }}</span><small class="status">● {{ account.status }}</small></article></template>
      <template v-else><p class="eyebrow">YOUR ACTIVITY</p><h1>Transactions</h1><article v-for="transaction in transactions" :key="transaction.id" class="item transaction"><div><strong>{{ transaction.transaction_type }}</strong><small>{{ transaction.transaction_reference }}</small></div><span :class="{ credit: Number(transaction.credit_amount) > 0 }">{{ money(transaction.credit_amount - transaction.debit_amount) }}</span></article><p v-if="!transactions.length">No transactions found.</p></template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { setApiBaseUrl } from './services/api'

const token = ref(localStorage.getItem('token'))
const username = ref('')
const password = ref('')
const serverUrl = ref(localStorage.getItem('bembankApiUrl') || process.env.QCLI_API_BASE_URL)
const user = ref(null)
const accounts = ref([])
const transactions = ref([])
const adminAccounts = ref([])
const page = ref('home')
const loading = ref(false)
const error = ref('')
const depositAmount = ref(null)
const depositing = ref(false)
const recipientAccountId = ref(null)
const transferAmount = ref(null)
const transferring = ref(false)
const total = computed(() => accounts.value.reduce((sum, account) => sum + Number(account.available_balance), 0))
const recipients = computed(() => adminAccounts.value.filter(account => account.id !== accounts.value[0]?.id))
const money = value => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(value || 0)

async function loadBanking() {
  loading.value = true
  error.value = ''
  try {
    const [me, accountList, transactionList] = await Promise.all([api.get('/customer/me'), api.get('/customer/accounts'), api.get('/customer/transactions')])
    user.value = me.data
    accounts.value = accountList.data
    transactions.value = transactionList.data
    if (me.data.username === 'espada') adminAccounts.value = (await api.get('/customer/admin/accounts')).data
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Cannot connect to the bank server.'
  } finally { loading.value = false }
}

async function login() {
  if (!/^https?:\/\/.+/.test(serverUrl.value)) {
    error.value = 'Enter a server address beginning with http:// or https://'
    return
  }
  loading.value = true
  error.value = ''
  try {
    setApiBaseUrl(serverUrl.value)
    localStorage.setItem('bembankApiUrl', serverUrl.value.replace(/\/+$/, ''))
    const body = new URLSearchParams({ username: username.value, password: password.value })
    const { data } = await api.post('/auth/login', body)
    localStorage.setItem('token', data.access_token)
    token.value = data.access_token
    await loadBanking()
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Cannot connect to the bank server.'
  } finally { loading.value = false }
}

async function logout() {
  try { await api.post('/auth/logout') } finally {
    localStorage.removeItem('token')
    token.value = ''
    user.value = null
    accounts.value = []
    transactions.value = []
  }
}

async function deposit() {
  if (!depositAmount.value || depositAmount.value <= 0) return
  depositing.value = true
  error.value = ''
  try {
    await api.post('/deposits/', {
      account_id: accounts.value[0].id,
      reference_number: `ESP-${Date.now()}`,
      amount: String(depositAmount.value),
      deposit_channel: 'CASH',
      remarks: 'Demo admin deposit',
    })
    depositAmount.value = null
    await loadBanking()
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not add demo money.'
  } finally { depositing.value = false }
}

async function transfer() {
  if (!recipientAccountId.value || !transferAmount.value || transferAmount.value <= 0) return
  transferring.value = true
  error.value = ''
  try {
    await api.post('/transfers/', {
      source_account_id: accounts.value[0].id,
      destination_account_id: recipientAccountId.value,
      transfer_reference: `BEM-${Date.now()}`,
      amount: String(transferAmount.value),
      transfer_type: 'INTERNAL',
      remarks: 'BEMBank demo send money',
    })
    transferAmount.value = null
    recipientAccountId.value = null
    page.value = 'transactions'
    await loadBanking()
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || 'Could not send demo money.'
  } finally { transferring.value = false }
}

onMounted(() => {
  document.getElementById('startup-status')?.remove()
  setApiBaseUrl(serverUrl.value)
  if (token.value) loadBanking()
})
</script>

<style>
* { box-sizing: border-box; } body { margin: 0; background: #020b1d; }
.app-shell { min-height: 100vh; background: radial-gradient(circle at 85% 0, #113f8a 0, transparent 29%), linear-gradient(145deg, #020b1d 0%, #06132b 62%, #020914 100%); color: #f5f8ff; font: 16px Arial, sans-serif; padding: 22px 18px 38px; }.login-card, .banking { max-width: 480px; margin: 22px auto; }.login-card { min-height: calc(100vh - 80px); display: flex; flex-direction: column; justify-content: center; padding: 30px 24px; }
.brand-mark, .mini-mark { display: grid; place-items: center; color: #72b5ff; background: linear-gradient(145deg, #102b69, #061437); border: 1px solid #2e66d4; font-weight: 800; box-shadow: 0 0 28px #1573ff36; }.brand-mark { width: 58px; height: 58px; border-radius: 18px; font-size: 30px; margin-bottom: 28px; }.mini-mark { width: 32px; height: 32px; border-radius: 10px; }.eyebrow { color: #82a5d9; font-size: 10px; font-weight: 700; letter-spacing: 1.4px; margin: 0 0 8px; }.muted, .demo-note { color: #88a0c7; }.demo-note { text-align: center; font-size: 12px; margin: 24px 0 0; }
.server-help { color: #7e9ac5; font-size: 11px; line-height: 1.4; margin: -12px 0 4px; }
h1 { margin: 0 0 7px; font-size: 29px; letter-spacing: -.7px; } h2 { margin: 0 0 8px; } label, input, select, button { display: block; width: 100%; } label { margin: 20px 0; color: #c8d8f3; font-size: 13px; font-weight: 700; } input, select { margin-top: 8px; padding: 14px; color: #f5f8ff; border: 1px solid #1d3e72; background: #07162f; border-radius: 10px; font-size: 16px; } select option { background: #07162f; }
button { border: 0; border-radius: 11px; padding: 14px; background: linear-gradient(135deg, #1267ff, #2f91ff); color: #fff; font-size: 16px; font-weight: 700; box-shadow: 0 8px 20px #0e63df33; } button:disabled { opacity: .6; }.error { color: #ff9d9d; font-weight: bold; }
header { display: flex; justify-content: space-between; align-items: center; font-size: 20px; margin-bottom: 26px; }.header-brand { display: flex; align-items: center; gap: 9px; }.header-brand small { display: block; color: #7392c4; font-size: 10px; margin-top: 2px; } button.link { width: auto; background: transparent; box-shadow: none; color: #7fafff; padding: 4px; font-size: 14px; }
nav { display: flex; gap: 4px; margin: 30px 0 12px; padding: 8px 5px; border: 1px solid #172d54; background: #07152b; border-radius: 17px; } nav button { display: flex; flex-direction: column; gap: 3px; align-items: center; padding: 8px 4px; border-radius: 10px; background: transparent; box-shadow: none; color: #7993bd; font-size: 17px; } nav button span { font-size: 10px; } nav button.active { background: #11336d; color: #79b3ff; }
.balance-card { color: #fff; background: linear-gradient(135deg, #164eff, #0b2496 70%, #101b73); border: 1px solid #3c71ff; border-radius: 20px; padding: 23px; margin: 22px 0; box-shadow: 0 16px 32px #0634d357; }.card-top { display: flex; justify-content: space-between; color: #c5d8ff; }.balance-card small { color: #bfd4ff; }.balance { display: block; font-size: 36px; margin: 14px 0; letter-spacing: -.9px; }.section-title { color: #c8d8f3; font-size: 14px; font-weight: 700; margin: 0 0 12px; }.item { display: flex; justify-content: space-between; align-items: center; gap: 12px; background: #08172f; border: 1px solid #172e55; border-radius: 15px; margin: 12px 0; padding: 17px; box-shadow: 0 5px 14px #00000026; }.item div { display: grid; gap: 5px; }.item strong { display: block; }.item span { font-size: 18px; font-weight: 700; }.item small { color: #7894bf; }.status, .credit { color: #55d7af !important; }.transaction span { color: #55d7af; }
.quick-actions { display: flex; gap: 9px; margin: 0 0 24px; }.quick-actions button { display: grid; gap: 7px; padding: 14px 5px; background: #091a35; border: 1px solid #19365f; box-shadow: none; color: #d8e6ff; font-size: 11px; }.quick-actions b { display: grid; place-items: center; width: 29px; height: 29px; margin: auto; border-radius: 9px; background: #123c87; color: #85b9ff; font-size: 19px; }
.deposit { background: #08172f; border: 1px solid #172e55; border-radius: 16px; margin-top: 24px; padding: 20px; box-shadow: 0 5px 14px #00000026; }.deposit h2 { font-size: 20px; }
</style>
