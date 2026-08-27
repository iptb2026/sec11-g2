<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-teal-8 text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>
          <q-icon name="support_agent" class="q-mr-sm" />
          Staff Portal
        </q-toolbar-title>
        <div class="q-mr-md text-caption">{{ auth.fullName }}</div>
        <q-btn flat dense icon="logout" label="Logout" @click="handleLogout" id="staff-logout" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header class="text-weight-bold text-teal-8">
          <q-icon name="support_agent" class="q-mr-sm" />
          Staff Operations
        </q-item-label>

        <q-item clickable v-ripple :to="{ name: 'StaffDashboard' }" active-class="bg-teal-1 text-teal-8">
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />
        <q-item-label header class="text-caption text-grey">ACCOUNT MANAGEMENT</q-item-label>

        <q-item clickable v-ripple :to="{ name: 'StaffAccounts' }" active-class="bg-teal-1 text-teal-8">
          <q-item-section avatar><q-icon name="account_box" /></q-item-section>
          <q-item-section>Accounts</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />
        <q-item-label header class="text-caption text-grey">TRANSACTIONS</q-item-label>

        <q-item clickable v-ripple :to="{ name: 'StaffDeposits' }" active-class="bg-teal-1 text-teal-8">
          <q-item-section avatar><q-icon name="savings" /></q-item-section>
          <q-item-section>Deposits</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'StaffWithdrawals' }" active-class="bg-teal-1 text-teal-8">
          <q-item-section avatar><q-icon name="money_off" /></q-item-section>
          <q-item-section>Withdrawals</q-item-section>
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
