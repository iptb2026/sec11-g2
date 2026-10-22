<template>
  <q-layout view="hHh Lpr lFf" class="bank-layout" :class="{ 'customer-layout': auth.isCustomer, 'customer-subpage': auth.isCustomer && route.path !== '/', 'customer-more-layout': auth.isCustomer && ['/customer/more', '/profile'].includes(route.path) }">
    <q-header class="bank-header">
      <q-toolbar class="bank-toolbar">
        <div v-if="auth.isCustomer && route.path !== '/'" class="mobile-page-header"><q-btn v-if="!['/customer/more', '/profile'].includes(route.path)" flat round icon="chevron_left" aria-label="Back to home" to="/" /><span v-else /><strong>{{ mobileTitle }}</strong><span /></div>
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
        <span class="demo-label">Simulated banking</span>
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
        <q-item clickable to="/" exact active-class="bank-nav-item--active" class="bank-nav-item">
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Overview</q-item-section>
        </q-item>
        <q-item clickable to="/requests" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon name="inbox" /></q-item-section><q-item-section>{{ auth.isCustomer ? 'Deposit / withdraw' : 'Customer requests' }}</q-item-section></q-item>

        <q-item v-if="!auth.isCustomer" clickable to="/staff/register" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon name="person_add" /></q-item-section><q-item-section>Register customer</q-item-section></q-item>
        <q-item clickable to="/statements" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon name="description" /></q-item-section><q-item-section>Account statements</q-item-section></q-item>
        <q-item v-if="auth.isCustomer" clickable to="/customer/other-banks" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon name="account_balance" /></q-item-section><q-item-section>Send to another bank</q-item-section></q-item>
        <q-item clickable to="/help" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon name="help_outline" /></q-item-section><q-item-section>Help & support</q-item-section></q-item>
        <template v-if="auth.isAdmin">
          <q-item-label header class="nav-section-label">Administration</q-item-label>
          <q-item clickable to="/admin/users" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="people" /></q-item-section>
            <q-item-section>Users</q-item-section>
          </q-item>
          <q-item clickable to="/admin/roles" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
            <q-item-section>Roles</q-item-section>
          </q-item>
          <q-item clickable to="/admin/account-types" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="category" /></q-item-section>
            <q-item-section>Account types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/banks" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="account_balance" /></q-item-section>
            <q-item-section>Banks</q-item-section>
          </q-item>
          <q-item clickable to="/admin/fee-types" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="sell" /></q-item-section>
            <q-item-section>Fee types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/audit-logs" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="history" /></q-item-section>
            <q-item-section>Audit log</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isAdmin || auth.isStaff">
          <q-item-label header class="nav-section-label">Banking</q-item-label>
          <q-item clickable to="/accounts" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>Accounts</q-item-section>
          </q-item>
          <q-item clickable to="/deposits" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="add_card" /></q-item-section>
            <q-item-section>Deposits</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawals" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="remove_circle" /></q-item-section>
            <q-item-section>Withdrawals</q-item-section>
          </q-item>
          <q-item clickable to="/transfers" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="swap_horiz" /></q-item-section>
            <q-item-section>Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/interbank-transfers" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="sync_alt" /></q-item-section>
            <q-item-section>Interbank transfers</q-item-section>
          </q-item>
          <q-item clickable to="/ledger-entries" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="menu_book" /></q-item-section>
            <q-item-section>Ledger</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawal-limits" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="speed" /></q-item-section>
            <q-item-section>Withdrawal limits</q-item-section>
          </q-item>
          <q-item clickable to="/interest-policies" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="percent" /></q-item-section>
            <q-item-section>Interest policies</q-item-section>
          </q-item>
          <q-item clickable to="/fee-records" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>Fee records</q-item-section>
          </q-item>
          <q-item clickable to="/interest-records" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="savings" /></q-item-section>
            <q-item-section>Interest records</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isCustomer">
          <q-item-label header class="nav-section-label">My banking</q-item-label>
          <q-item v-for="item in extraLinks" :key="item.to" clickable :to="item.to" active-class="bank-nav-item--active" class="bank-nav-item"><q-item-section avatar><q-icon :name="item.icon" /></q-item-section><q-item-section>{{ item.label }}</q-item-section></q-item>
          <q-item clickable to="/my-account" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>My account</q-item-section>
          </q-item>
          <q-item clickable to="/customer/transfers" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="swap_horiz" /></q-item-section>
            <q-item-section>Send funds</q-item-section>
          </q-item>
          <q-item clickable to="/customer/bill-payments" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>Pay bills</q-item-section>
          </q-item>
          <q-item clickable to="/customer/investments" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="trending_up" /></q-item-section>
            <q-item-section>Investments</q-item-section>
          </q-item>
          <q-item clickable to="/my-transactions" active-class="bank-nav-item--active" class="bank-nav-item">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>Transactions</q-item-section>
          </q-item>
        </template>
      </q-list>
      <div class="drawer-footer"><q-icon name="shield" size="22px" /><div><strong>A little more peace of mind.</strong><p>Never share your password or PIN.</p></div></div>
    </q-drawer>

    <q-page-container class="bank-content">
      <router-view />
    </q-page-container>
    <nav v-if="auth.isCustomer" class="mobile-bank-nav" aria-label="Main navigation"><q-btn flat stack icon="home" label="Home" to="/" exact /><q-btn flat stack icon="account_balance_wallet" label="Accounts" to="/my-account" /><q-btn flat stack icon="qr_code_scanner" label="Scan" class="mobile-scan-button" to="/customer/transfers?scan=1" /><q-btn flat stack icon="credit_card" label="Cards" to="/customer/cards" /><q-btn flat stack icon="menu" label="More" to="/customer/more" :class="{ 'q-router-link--active': route.path === '/profile' }" /></nav>
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

const extraLinks = [
  { label: 'Scan QR', icon: 'qr_code_scanner', to: '/customer/transfers?scan=1' },
  { label: 'Buy load', icon: 'phone_android', to: '/customer/mobile-load' },
  { label: 'My cards', icon: 'credit_card', to: '/customer/cards' },
  { label: 'Savings goals', icon: 'savings', to: '/customer/savings' },
  { label: 'Activity alerts', icon: 'notifications_none', to: '/customer/notifications' },
  { label: 'Profile & security', icon: 'manage_accounts', to: '/profile' },
]

const leftDrawerOpen = ref(false)
const auth = useAuthStore()
const $q = useQuasar()
const isMobileCustomer = computed(() => auth.isCustomer && $q.screen.width <= 700)
watch(isMobileCustomer, () => { leftDrawerOpen.value = false })
onMounted(async () => { try { auth.profilePhoto = (await api.get('/auth/profile-photo')).data.profile_photo } catch { auth.profilePhoto = null } })
watchEffect(() => applyPreferences(preferences(auth.userId)))
const router = useRouter()
const route = useRoute()
const mobileTitle = computed(() => ({ '/customer/more': 'Profile', '/customer/transfers': 'Send Money', '/my-account': 'My Accounts', '/my-transactions': 'Transaction History', '/customer/cards': 'My Cards', '/profile': 'Profile', '/customer/savings': 'Savings Goals', '/customer/notifications': 'Notifications', '/customer/mobile-load': 'Buy Load', '/customer/bill-payments': 'Pay Bills', '/customer/investments': 'Investments', '/help': 'Help & Support', '/statements': 'Account Statements', '/requests': 'Deposit / Withdraw', '/customer/other-banks': 'Send to Another Bank' }[route.path] || 'Bembank'))
watch(() => route.fullPath, () => { leftDrawerOpen.value = false })
const userInitials = computed(() => (auth.fullName || auth.username || 'U')
  .split(/\s+/)
  .filter(Boolean)
  .slice(0, 2)
  .map((part) => part[0])
  .join('')
  .toUpperCase())

async function onLogout () {
  await auth.logout()
  router.push('/login')
}
</script>
