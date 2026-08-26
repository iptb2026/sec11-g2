<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Welcome, {{ auth.fullName || auth.username }}</div>

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <div v-else class="row q-col-gutter-md">
      <div v-for="card in cards" :key="card.label" class="col-12 col-sm-6 col-md-3">
        <q-card bordered class="cursor-pointer" @click="card.to && router.push(card.to)">
          <q-card-section class="row items-center no-wrap">
            <q-icon :name="card.icon" size="36px" :color="card.color" class="q-mr-md" />
            <div>
              <div class="text-h5">{{ card.value }}</div>
              <div class="text-caption text-grey-7">{{ card.label }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-banner v-if="auth.isCustomer" class="bg-blue-1 q-mt-md" rounded>
      <template #avatar><q-icon name="info" color="primary" /></template>
      Use the menu on the left to view your account balance or your transaction history.
    </q-banner>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(true)
const cards = ref([])

async function loadAdminCards () {
  const [roles, users, accounts, banks] = await Promise.all([
    api.get('/roles/'),
    api.get('/users/'),
    api.get('/accounts/'),
    api.get('/banks/'),
  ])
  cards.value = [
    { label: 'Roles', value: roles.data.length, icon: 'admin_panel_settings', color: 'primary', to: '/admin/roles' },
    { label: 'Users', value: users.data.length, icon: 'people', color: 'primary', to: '/admin/users' },
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', color: 'primary', to: '/accounts' },
    { label: 'Registered Banks', value: banks.data.length, icon: 'account_balance', color: 'primary', to: '/admin/banks' },
  ]
}

async function loadStaffCards () {
  const [accounts, deposits, withdrawals, interbank] = await Promise.all([
    api.get('/accounts/'),
    api.get('/deposits/'),
    api.get('/withdrawals/'),
    api.get('/interbank-transfers/'),
  ])
  const pending = interbank.data.filter((i) => i.status === 'PROCESSING').length
  cards.value = [
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', color: 'primary', to: '/accounts' },
    { label: 'Deposits Recorded', value: deposits.data.length, icon: 'add_card', color: 'positive', to: '/deposits' },
    { label: 'Withdrawals Recorded', value: withdrawals.data.length, icon: 'remove_circle', color: 'negative', to: '/withdrawals' },
    { label: 'Interbank Pending', value: pending, icon: 'sync_alt', color: 'warning', to: '/interbank-transfers' },
  ]
}

async function loadCustomerCards () {
  const { data: allAccounts } = await api.get('/accounts/')
  const mine = allAccounts.filter((a) => a.customer_id === auth.userId)
  const totalBalance = mine.reduce((sum, a) => sum + Number(a.available_balance), 0)
  cards.value = [
    { label: 'My Accounts', value: mine.length, icon: 'account_box', color: 'primary', to: '/my-account' },
    {
      label: 'Total Available Balance',
      value: `₱${totalBalance.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`,
      icon: 'payments',
      color: 'positive',
      to: '/my-account',
    },
  ]
}

onMounted(async () => {
  try {
    if (auth.isAdmin) await loadAdminCards()
    else if (auth.isStaff) await loadStaffCards()
    else if (auth.isCustomer) await loadCustomerCards()
  } finally {
    loading.value = false
  }
})
</script>
