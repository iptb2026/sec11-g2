<template>
  <q-layout view="hHh Lpr lFf" class="bank-layout" :class="{ 'customer-layout': auth.isCustomer, 'customer-subpage': auth.isCustomer && route.path !== '/', 'customer-more-layout': auth.isCustomer && route.path === '/profile' }">
    <q-header class="bank-header">
      <q-toolbar class="bank-toolbar">
        <div v-if="auth.isCustomer && route.path !== '/'" class="mobile-page-header"><q-btn v-if="route.path !== '/profile'" flat round icon="chevron_left" aria-label="Back to home" to="/" /><span v-else /><strong>{{ mobileTitle }}</strong><span /></div>
        <div v-if="auth.isCustomer" class="mobile-customer-greeting"><ProfileAvatar size="38px" /><div><small>Welcome back,</small><strong>{{ auth.fullName || auth.username }}</strong></div></div>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Toggle navigation"
          title="Toggle navigation"
          class="header-icon-btn"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />
        <div class="bank-brand">
          <div class="brand-mark"><BankLogo /></div>
          <div class="brand-copy">
            <span class="brand-name">bembank<span class="brand-dot">.</span></span>
            <span class="brand-caption">Banking made simple</span>
          </div>
        </div>
        <div class="header-spacer" />
        <q-btn v-if="!auth.isCustomer" flat round icon="manage_accounts" aria-label="Profile and security" to="/profile" />
        <q-btn v-if="auth.isCustomer" flat round icon="notifications_none" aria-label="Account activity" to="/customer/notifications" />
        <div class="header-user">
          <ProfileAvatar size="36px" />
          <div class="header-user-copy">
            <span class="header-user-name">{{ auth.fullName || auth.username }}</span>
            <span class="header-user-role">{{ auth.roleName }}</span>
          </div>
        </div>
        <q-btn
          v-if="!auth.isCustomer"
          flat
          dense
          round
          icon="logout"
          aria-label="Sign out"
          title="Sign out"
          class="header-icon-btn"
          @click="onLogout"
        />
      </q-toolbar>
    </q-header>

    <q-drawer v-if="!auth.isCustomer || !isMobileCustomer" v-model="leftDrawerOpen" show-if-above bordered :width="252" :breakpoint="auth.isCustomer ? 700 : 960" class="bank-drawer">
      <div class="drawer-workspace">
        <div class="drawer-workspace-label">Your workspace</div>
        <div class="drawer-workspace-name">{{ auth.isCustomer ? 'Personal banking' : auth.isAdmin ? 'Administration' : 'Banking operations' }}</div>
      </div>
      <q-separator class="drawer-divider" />
      <q-list dense class="nav-list">
        <q-input v-if="!auth.isCustomer" v-model="navSearch" dense outlined clearable debounce="100" placeholder="Find a page" aria-label="Find a page" class="nav-search">
          <template #prepend><q-icon name="search" size="19px" /></template>
        </q-input>
        <q-item v-for="item in primaryLinks" :key="item.to" clickable :to="item.to" :exact="item.to === '/'" active-class="bank-nav-item--active" class="bank-nav-item">
          <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
          <q-item-section>{{ item.label }}</q-item-section>
        </q-item>

        <template v-if="!auth.isCustomer">
          <q-item-label header class="nav-section-label">Workspace</q-item-label>
          <q-expansion-item v-for="group in filteredStaffGroups" :key="`${group.label}-${navSearch}`" :icon="group.icon" :label="group.label" :default-opened="Boolean(navSearch) || group.links.some(link => route.path === link.to)" header-class="bank-nav-item nav-group" expand-icon-class="nav-expand-icon">
            <q-item v-for="item in group.links" :key="item.to" clickable :to="item.to" active-class="bank-nav-item--active" class="bank-nav-item nav-child">
              <q-item-section>{{ item.label }}</q-item-section>
            </q-item>
          </q-expansion-item>
        </template>

        <template v-else>
          <q-item-label header class="nav-section-label">More</q-item-label>
          <q-item v-for="item in customerMoreLinks" :key="item.to" clickable :to="item.to" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
            <q-item-section>{{ item.label }}</q-item-section>
          </q-item>
        </template>
      </q-list>
      <div class="drawer-footer"><q-icon name="shield" size="22px" /><div><strong>A little more peace of mind.</strong><p>Never share your password or PIN.</p></div></div>
    </q-drawer>

    <q-page-container class="bank-content">
      <router-view />
    </q-page-container>
    <nav v-if="auth.isCustomer" class="mobile-bank-nav" aria-label="Main navigation"><q-btn flat stack icon="home" label="Home" to="/" exact /><q-btn flat stack icon="account_balance_wallet" label="Accounts" to="/my-account" /><q-btn flat stack icon="qr_code_scanner" label="Scan" class="mobile-scan-button" to="/customer/transfers?scan=1" /><q-btn flat stack icon="credit_card" label="Cards" to="/customer/cards" /><q-btn flat stack icon="menu" label="More" to="/profile" /></nav>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, ref, watch, watchEffect } from 'vue'
import { useQuasar } from 'quasar'
import ProfileAvatar from '@/components/ProfileAvatar.vue'
import api from '@/services/api'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import { preferences, applyPreferences } from '@/utils/preferences'
import BankLogo from '@/components/BankLogo.vue'

const leftDrawerOpen = ref(false)
const navSearch = ref('')
const auth = useAuthStore()
const $q = useQuasar()
const primaryLinks = computed(() => auth.isCustomer ? [
  { label: 'Home', icon: 'home', to: '/' },
  { label: 'Accounts', icon: 'account_balance_wallet', to: '/my-account' },
  { label: 'Pay & transfer', icon: 'swap_horiz', to: '/customer/transfers' },
  { label: 'Transactions', icon: 'receipt_long', to: '/my-transactions' },
  { label: 'Cards', icon: 'credit_card', to: '/customer/cards' },
] : [
  { label: 'Overview', icon: 'space_dashboard', to: '/' },
  { label: 'Customer requests', icon: 'inbox', to: '/requests' },
])
const adminGroups = [
  { label: 'People & access', icon: 'manage_accounts', links: [{ label: 'Users', to: '/admin/users' }, { label: 'Roles & permissions', to: '/admin/roles' }, { label: 'Audit trail', to: '/admin/audit-logs' }] },
  { label: 'Products & rules', icon: 'tune', links: [{ label: 'Account types', to: '/admin/account-types' }, { label: 'Partner banks', to: '/admin/banks' }, { label: 'Fee types', to: '/admin/fee-types' }, { label: 'Withdrawal limits', to: '/withdrawal-limits' }, { label: 'Interest policies', to: '/interest-policies' }] },
]
const operationsGroups = [
  { label: 'Customers & accounts', icon: 'group', links: [{ label: 'Register customer', to: '/staff/register' }, { label: 'Accounts', to: '/accounts' }, { label: 'Statements', to: '/statements' }] },
  { label: 'Transactions', icon: 'currency_exchange', links: [{ label: 'Deposits', to: '/deposits' }, { label: 'Withdrawals', to: '/withdrawals' }, { label: 'Internal transfers', to: '/transfers' }, { label: 'Interbank transfers', to: '/interbank-transfers' }] },
  { label: 'Records & settlement', icon: 'receipt_long', links: [{ label: 'Ledger', to: '/ledger-entries' }, { label: 'Fee records', to: '/fee-records' }, { label: 'Interest records', to: '/interest-records' }] },
]
const staffGroups = computed(() => auth.isAdmin ? [...adminGroups, ...operationsGroups] : operationsGroups)
const filteredStaffGroups = computed(() => {
  const query = String(navSearch.value || '').trim().toLocaleLowerCase()
  if (!query) return staffGroups.value
  return staffGroups.value
    .map(group => ({ ...group, links: group.links.filter(link => `${group.label} ${link.label}`.toLocaleLowerCase().includes(query)) }))
    .filter(group => group.links.length)
})
const customerMoreLinks = [
  { label: 'Pay bills', icon: 'receipt_long', to: '/customer/bill-payments' },
  { label: 'Send to another bank', icon: 'account_balance', to: '/customer/other-banks' },
  { label: 'Statements', icon: 'description', to: '/statements' },
  { label: 'Help & support', icon: 'help_outline', to: '/help' },
  { label: 'Profile & security', icon: 'manage_accounts', to: '/profile' },
]
const isMobileCustomer = computed(() => auth.isCustomer && $q.screen.width <= 700)
watch(isMobileCustomer, () => { leftDrawerOpen.value = false })
onMounted(async () => { try { auth.profilePhoto = (await api.get('/auth/profile-photo')).data.profile_photo } catch { auth.profilePhoto = null } })
watchEffect(() => applyPreferences(preferences(auth.userId)))
const router = useRouter()
const route = useRoute()
const mobileTitle = computed(() => ({ '/customer/transfers': 'Send Money', '/my-account': 'My Accounts', '/my-transactions': 'Transaction History', '/customer/cards': 'My Cards', '/profile': 'Profile', '/customer/notifications': 'Notifications', '/customer/bill-payments': 'Pay Bills', '/help': 'Help & Support', '/statements': 'Account Statements', '/requests': 'Deposit / Withdraw', '/customer/other-banks': 'Send to Another Bank' }[route.path] || 'Bembank'))
watch(() => route.fullPath, () => { leftDrawerOpen.value = false })
async function onLogout () {
  await auth.logout()
  router.push('/login')
}
</script>
