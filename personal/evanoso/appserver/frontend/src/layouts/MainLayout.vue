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
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
          <q-icon name="account_balance" class="q-mr-sm" />
          Mini Banking System
        </q-toolbar-title>

        <q-chip
          v-if="auth.roleName"
          square
          color="white"
          text-color="primary"
          icon="badge"
          class="q-mr-md"
        >
          {{ auth.roleName }}
        </q-chip>

        <div class="q-mr-md">{{ auth.fullName || auth.username }}</div>

        <q-btn flat dense round icon="logout" aria-label="Logout" @click="onLogout" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Navigation</q-item-label>

        <q-item clickable to="/" exact>
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <template v-if="auth.isAdmin">
          <q-separator spaced />
          <q-item-label header>System Configuration</q-item-label>
          <q-item clickable to="/admin/roles">
            <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
            <q-item-section>Roles</q-item-section>
          </q-item>
          <q-item clickable to="/admin/account-types">
            <q-item-section avatar><q-icon name="category" /></q-item-section>
            <q-item-section>Account Types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/banks">
            <q-item-section avatar><q-icon name="account_balance" /></q-item-section>
            <q-item-section>Banks</q-item-section>
          </q-item>
          <q-item clickable to="/admin/fee-types">
            <q-item-section avatar><q-icon name="sell" /></q-item-section>
            <q-item-section>Fee Types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/users">
            <q-item-section avatar><q-icon name="people" /></q-item-section>
            <q-item-section>Users</q-item-section>
          </q-item>
          <q-item clickable to="/admin/audit-logs">
            <q-item-section avatar><q-icon name="history" /></q-item-section>
            <q-item-section>Audit Logs</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isAdmin || auth.isStaff">
          <q-separator spaced />
          <q-item-label header>Banking Operations</q-item-label>
          <q-item clickable to="/accounts">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>Accounts</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawal-limits">
            <q-item-section avatar><q-icon name="speed" /></q-item-section>
            <q-item-section>Withdrawal Limits</q-item-section>
          </q-item>
          <q-item clickable to="/interest-policies">
            <q-item-section avatar><q-icon name="percent" /></q-item-section>
            <q-item-section>Interest Policies</q-item-section>
          </q-item>
          <q-item clickable to="/deposits">
            <q-item-section avatar><q-icon name="add_card" /></q-item-section>
            <q-item-section>Deposits</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawals">
            <q-item-section avatar><q-icon name="remove_circle" /></q-item-section>
            <q-item-section>Withdrawals</q-item-section>
          </q-item>
          <q-item clickable to="/transfers">
            <q-item-section avatar><q-icon name="swap_horiz" /></q-item-section>
            <q-item-section>Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/interbank-transfers">
            <q-item-section avatar><q-icon name="sync_alt" /></q-item-section>
            <q-item-section>Interbank Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/fee-records">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>Fee Records</q-item-section>
          </q-item>
          <q-item clickable to="/interest-records">
            <q-item-section avatar><q-icon name="savings" /></q-item-section>
            <q-item-section>Interest Records</q-item-section>
          </q-item>
          <q-item clickable to="/ledger-entries">
            <q-item-section avatar><q-icon name="menu_book" /></q-item-section>
            <q-item-section>Ledger Entries</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isCustomer">
          <q-separator spaced />
          <q-item-label header>My Banking</q-item-label>
          <q-item clickable to="/my-account">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>My Account</q-item-section>
          </q-item>
          <q-item clickable to="/my-transactions">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>My Transactions</q-item-section>
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
import { useAuthStore } from '@/stores/auth-store'

const leftDrawerOpen = ref(false)
const auth = useAuthStore()
const router = useRouter()

function onLogout () {
  auth.logout()
  router.push('/login')
}
</script>
