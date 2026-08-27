<template>
  <div>
    <!-- Welcome Banner -->
    <q-card class="bg-deep-purple-8 text-white q-mb-md" flat>
      <q-card-section class="row items-center justify-between">
        <div>
          <div class="text-h5 text-weight-bold">Welcome back, {{ auth.user?.first_name }}!</div>
          <div class="text-subtitle2 text-deep-purple-2">Account Status: {{ auth.user?.account_status }}</div>
        </div>
        <q-icon name="account_balance" size="48px" class="text-deep-purple-2" />
      </q-card-section>
    </q-card>

    <!-- Stat Cards -->
    <div class="row q-gutter-md q-mb-md">
      <q-card class="col-12 col-sm-5" flat bordered>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="account_balance_wallet" size="40px" color="deep-purple" />
          <div>
            <div class="text-caption text-grey">Total Available Balance</div>
            <div class="text-h5 text-weight-bold text-deep-purple-9">
              ₱{{ totalBalance.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </div>
          </div>
        </q-card-section>
      </q-card>

      <q-card class="col-12 col-sm-5" flat bordered>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="credit_card" size="40px" color="teal" />
          <div>
            <div class="text-caption text-grey">My Accounts</div>
            <div class="text-h5 text-weight-bold text-teal-9">
              {{ myAccounts.length }} Active
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Accounts Overview -->
    <div class="text-h6 text-weight-bold q-mb-sm">My Accounts Overview</div>
    <q-table
      :rows="myAccounts"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
      dense
      no-data-label="You do not have any registered accounts yet."
    >
      <template v-slot:body-cell-available_balance="props">
        <q-td :props="props" class="text-right text-weight-bold text-primary">
          ₱{{ Number(props.row.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-chip
            dense
            size="sm"
            :color="props.row.status === 'ACTIVE' ? 'green-1' : 'orange-1'"
            :text-color="props.row.status === 'ACTIVE' ? 'green-9' : 'orange-9'"
          >
            {{ props.row.status }}
          </q-chip>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const $q = useQuasar()
const auth = useAuthStore()

const myAccounts = ref([])
const loading = ref(false)

const columns = [
  { name: 'account_number', label: 'Account Number', field: 'account_number', align: 'left', sortable: true },
  { name: 'currency_code', label: 'Currency', field: 'currency_code', align: 'center' },
  { name: 'available_balance', label: 'Available Balance', field: 'available_balance', align: 'right', sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'branch_code', label: 'Branch', field: 'branch_code', align: 'left' },
]

const totalBalance = computed(() => {
  return myAccounts.value.reduce((sum, acc) => sum + Number(acc.available_balance || 0), 0)
})

async function fetchMyAccounts() {
  loading.value = true
  try {
    const { data } = await api.get('/accounts/my')
    myAccounts.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load personal accounts',
    })
  } finally {
    loading.value = false
  }
}

onMounted(fetchMyAccounts)
</script>
