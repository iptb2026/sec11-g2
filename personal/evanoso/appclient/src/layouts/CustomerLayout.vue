<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-deep-purple-8 text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>
          <q-icon name="person" class="q-mr-sm" />
          My Banking
        </q-toolbar-title>
        <div class="q-mr-md text-caption">{{ auth.fullName }}</div>
        <q-btn flat dense icon="logout" label="Logout" @click="handleLogout" id="customer-logout" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header class="text-weight-bold text-deep-purple-8">
          <q-icon name="person" class="q-mr-sm" />
          My Banking
        </q-item-label>

        <q-item clickable v-ripple :to="{ name: 'CustomerDashboard' }" active-class="bg-purple-1 text-deep-purple-8">
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'CustomerAccounts' }" active-class="bg-purple-1 text-deep-purple-8">
          <q-item-section avatar><q-icon name="account_balance_wallet" /></q-item-section>
          <q-item-section>My Accounts</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'CustomerTransactions' }" active-class="bg-purple-1 text-deep-purple-8">
          <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
          <q-item-section>Transactions</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-page class="q-pa-md">
        <router-view />
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const leftDrawerOpen = ref(true)

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>
