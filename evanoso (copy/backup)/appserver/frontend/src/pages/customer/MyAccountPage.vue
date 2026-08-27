<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">My Account</div>

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <div v-else-if="accounts.length === 0" class="text-grey-7">
      No account is registered under your profile yet. Ask a bank staff member to open one for you.
    </div>

    <div v-else class="row q-col-gutter-md">
      <div v-for="acc in accounts" :key="acc.id" class="col-12 col-md-6">
        <q-card bordered>
          <q-card-section class="bg-primary text-white">
            <div class="text-subtitle2">Account Number</div>
            <div class="text-h6">{{ acc.account_number }}</div>
          </q-card-section>
          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <div class="text-caption text-grey-7">Available Balance</div>
                <div class="text-h5 text-positive">₱{{ format(acc.available_balance) }}</div>
              </div>
              <div class="col-6">
                <div class="text-caption text-grey-7">Ledger Balance</div>
                <div class="text-h5">₱{{ format(acc.ledger_balance) }}</div>
              </div>
            </div>
            <q-separator class="q-my-sm" />
            <div class="row q-col-gutter-sm text-body2">
              <div class="col-6"><span class="text-grey-7">Currency:</span> {{ acc.currency_code }}</div>
              <div class="col-6"><span class="text-grey-7">Branch:</span> {{ acc.branch_code || '—' }}</div>
              <div class="col-6">
                <span class="text-grey-7">Status:</span>
                <q-badge :color="acc.status === 'ACTIVE' ? 'positive' : 'grey'">{{ acc.status }}</q-badge>
              </div>
              <div class="col-6"><span class="text-grey-7">Opened:</span> {{ acc.opened_at?.slice(0, 10) }}</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const accounts = ref([])
const loading = ref(true)

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(async () => {
  try {
    const { data } = await api.get('/accounts/')
    accounts.value = data.filter((a) => a.customer_id === auth.userId)
  } finally {
    loading.value = false
  }
})
</script>
