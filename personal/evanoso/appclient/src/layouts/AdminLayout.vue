<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>
          <q-icon name="admin_panel_settings" class="q-mr-sm" />
          Admin Panel
        </q-toolbar-title>
        <div class="q-mr-md text-caption">{{ auth.fullName }}</div>
        <q-btn flat dense icon="logout" label="Logout" @click="handleLogout" id="admin-logout" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header class="text-weight-bold text-primary">
          <q-icon name="admin_panel_settings" class="q-mr-sm" />
          Administration
        </q-item-label>

        <q-item clickable v-ripple :to="{ name: 'AdminDashboard' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />
        <q-item-label header class="text-caption text-grey">IDENTITY & ACCESS</q-item-label>

        <q-item clickable v-ripple :to="{ name: 'AdminUsers' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="people" /></q-item-section>
          <q-item-section>Users</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'AdminRoles' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="security" /></q-item-section>
          <q-item-section>Roles</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'AdminSessions' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="devices" /></q-item-section>
          <q-item-section>Sessions</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'AdminAuditLogs' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="history" /></q-item-section>
          <q-item-section>Audit Logs</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />
        <q-item-label header class="text-caption text-grey">REFERENCE DATA</q-item-label>

        <q-item clickable v-ripple :to="{ name: 'AdminBanks' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="account_balance" /></q-item-section>
          <q-item-section>Banks</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'AdminAccountTypes' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="category" /></q-item-section>
          <q-item-section>Account Types</q-item-section>
        </q-item>

        <q-item clickable v-ripple :to="{ name: 'AdminFeeTypes' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="payments" /></q-item-section>
          <q-item-section>Fee Types</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />
        <q-item-label header class="text-caption text-grey">ACCOUNTS</q-item-label>

        <q-item clickable v-ripple :to="{ name: 'AdminAccounts' }" active-class="bg-blue-1 text-primary">
          <q-item-section avatar><q-icon name="account_box" /></q-item-section>
          <q-item-section>Accounts</q-item-section>
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
