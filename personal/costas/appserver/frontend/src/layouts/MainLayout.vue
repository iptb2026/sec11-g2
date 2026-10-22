<template>
  <q-layout view="lHh Lpr lFf">
    <q-header class="app-header"><q-toolbar><q-btn flat round dense icon="menu" @click="drawer = !drawer" /><q-toolbar-title>Mini Banking System</q-toolbar-title><q-chip outline color="white" :label="auth.roleCode" /><q-btn flat round icon="logout" aria-label="Log out" @click="logout" /></q-toolbar></q-header>
    <q-drawer v-model="drawer" show-if-above bordered><q-list padding><q-item-label header>Workspace</q-item-label><q-item v-for="item in visibleItems" :key="item.path" clickable v-ripple :to="item.path" exact-active-class="nav-active"><q-item-section avatar><q-icon :name="item.icon" /></q-item-section><q-item-section>{{ item.label }}</q-item-section></q-item></q-list></q-drawer>
    <q-page-container><router-view /></q-page-container>
  </q-layout>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth-store'
const drawer = ref(true); const auth = useAuthStore(); const router = useRouter()
const items = [
  { path: '/', label: 'Dashboard', icon: 'dashboard', roles: ['ADMIN', 'STAFF', 'CUSTOMER'] },
  { path: '/roles', label: 'Roles', icon: 'badge', roles: ['ADMIN'] }, { path: '/account-types', label: 'Account Types', icon: 'category', roles: ['ADMIN'] },
  { path: '/banks', label: 'Banks', icon: 'account_balance', roles: ['ADMIN'] }, { path: '/fee-types', label: 'Fee Types', icon: 'receipt_long', roles: ['ADMIN'] },
  { path: '/users', label: 'Users', icon: 'people', roles: ['ADMIN'] }, { path: '/accounts', label: 'Accounts', icon: 'credit_card', roles: ['ADMIN', 'STAFF'] },
  { path: '/audit-logs', label: 'Audit Logs', icon: 'fact_check', roles: ['ADMIN'] }, { path: '/withdrawal-limits', label: 'Withdrawal Limits', icon: 'speed', roles: ['ADMIN', 'STAFF'] },
  { path: '/interest-policies', label: 'Interest Policies', icon: 'percent', roles: ['ADMIN', 'STAFF'] }, { path: '/deposits', label: 'Deposits', icon: 'south', roles: ['ADMIN', 'STAFF'] },
  { path: '/withdrawals', label: 'Withdrawals', icon: 'north', roles: ['ADMIN', 'STAFF'] }, { path: '/transfers', label: 'Transfers', icon: 'swap_horiz', roles: ['ADMIN', 'STAFF'] },
  { path: '/interbank-transfers', label: 'Interbank Transfers', icon: 'public', roles: ['ADMIN', 'STAFF'] }, { path: '/fee-records', label: 'Fee Records', icon: 'receipt', roles: ['ADMIN', 'STAFF'] },
  { path: '/interest-records', label: 'Interest Records', icon: 'trending_up', roles: ['ADMIN', 'STAFF'] }, { path: '/ledger-entries', label: 'Ledger Entries', icon: 'list_alt', roles: ['ADMIN', 'STAFF'] },
  { path: '/my-account', label: 'My Account', icon: 'account_circle', roles: ['CUSTOMER'] }, { path: '/my-transactions', label: 'My Transactions', icon: 'history', roles: ['CUSTOMER'] }
]
const visibleItems = computed(() => items.filter((item) => item.roles.includes(auth.roleCode)))
function logout () { auth.logout(); router.push('/login') }
</script>
