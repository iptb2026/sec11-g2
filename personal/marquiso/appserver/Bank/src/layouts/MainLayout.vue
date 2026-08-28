<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> Quasar App </q-toolbar-title>

        <q-btn
          flat
          round
          dense
          icon="logout"
          aria-label="Log out"
          @click="logout"
        >
          <q-tooltip>Log out</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header> Essential Links </q-item-label>

        <EssentialLink
          v-for="link in linksList"
          :key="link.label"
          v-bind="link"
        />
        <template v-if="['ADMIN', 'MANAGER'].includes(authStore.roleCode)">
          <q-item-label header>Management</q-item-label>
          <q-item v-if="authStore.isAdmin" clickable to="/admin/users">
            <q-item-section avatar><q-icon name="manage_accounts" /></q-item-section>
            <q-item-section>Users</q-item-section>
          </q-item>
          <q-item v-for="link in managerLinks" :key="link.label" clickable :to="link.to">
            <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
            <q-item-section>{{ link.label }}</q-item-section>
          </q-item>
        </template>
        <template v-if="['ADMIN', 'STAFF'].includes(authStore.roleCode)">
          <q-item-label header>Staff operations</q-item-label>
          <q-item v-for="link in staffLinks" :key="link.label" clickable :to="link.to">
            <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
            <q-item-section>{{ link.label }}</q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import EssentialLink from '@/components/EssentialLink.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const linksList = [
  {
    label: 'Docs',
    caption: 'quasar.dev',
    icon: 'school',
    link: 'https://quasar.dev'
  },
  {
    label: 'GitHub',
    caption: 'github.com/quasarframework',
    icon: 'code',
    link: 'https://github.com/quasarframework'
  },
  {
    label: 'Discord Chat Channel',
    caption: 'chat.quasar.dev',
    icon: 'chat',
    link: 'https://chat.quasar.dev'
  },
  {
    label: 'Forum',
    caption: 'forum.quasar.dev',
    icon: 'record_voice_over',
    link: 'https://forum.quasar.dev'
  },
  {
    label: 'Twitter',
    caption: '@quasarframework',
    icon: 'rss_feed',
    link: 'https://twitter.quasar.dev'
  },
  {
    label: 'Facebook',
    caption: '@QuasarFramework',
    icon: 'public',
    link: 'https://facebook.quasar.dev'
  },
  {
    label: 'Quasar Awesome',
    caption: 'Community Quasar projects',
    icon: 'favorite',
    link: 'https://awesome.quasar.dev'
  }
]

const leftDrawerOpen = ref(false)
const router = useRouter()
const authStore = useAuthStore()
const managerLinks = [
  { label: 'Dashboard', icon: 'dashboard', to: '/manager/dashboard' },
  { label: 'Accounts', icon: 'account_balance_wallet', to: '/manager/accounts' },
  { label: 'Transactions', icon: 'receipt_long', to: '/manager/transactions' },
  { label: 'Transfers', icon: 'swap_horiz', to: '/manager/transfers' },
  { label: 'Interbank transfers', icon: 'account_balance', to: '/manager/interbank-transfers' },
  { label: 'Interest policies', icon: 'percent', to: '/manager/interest-policies' },
  { label: 'Fee records', icon: 'request_quote', to: '/manager/fee-records' },
  { label: 'Ledger entries', icon: 'menu_book', to: '/manager/ledger-entries' },
]
const staffLinks = [
  { label: 'Dashboard', icon: 'dashboard', to: '/staff/dashboard' },
  { label: 'Accounts', icon: 'account_balance_wallet', to: '/staff/accounts' },
  { label: 'Deposits', icon: 'add_card', to: '/staff/deposits' },
  { label: 'Withdrawals', icon: 'payments', to: '/staff/withdrawals' },
  { label: 'Transfers', icon: 'swap_horiz', to: '/staff/transfers' },
  { label: 'Interbank transfers', icon: 'account_balance', to: '/staff/interbank-transfers' },
]

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

async function logout () {
  try {
    if (authStore.token) {
      await api.post('/auth/logout')
    }
  } finally {
    authStore.logout()
    await router.push('/login')
  }
}
</script>
