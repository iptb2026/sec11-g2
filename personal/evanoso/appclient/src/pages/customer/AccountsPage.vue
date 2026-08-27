<template>
  <div>
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">My Bank Accounts</div>
        <div class="text-caption text-grey">View your active bank accounts and balances</div>
      </div>
      <q-btn
        color="deep-purple-8"
        icon="sync_alt"
        label="Transfer Money"
        @click="openTransferDialog"
        :disable="myAccounts.length === 0"
        id="customer-transfer-btn"
      />
    </div>

    <!-- Account Cards Grid -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div v-for="acc in myAccounts" :key="acc.id" class="col-12 col-md-6">
        <q-card flat bordered class="account-card">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="text-overline text-deep-purple">ACCOUNT NO.</div>
              <q-chip
                dense
                size="sm"
                :color="acc.status === 'ACTIVE' ? 'green-1' : 'orange-1'"
                :text-color="acc.status === 'ACTIVE' ? 'green-9' : 'orange-9'"
              >
                {{ acc.status }}
              </q-chip>
            </div>
            <div class="text-h6 text-weight-bold text-mono">{{ acc.account_number }}</div>
            <div class="text-caption text-grey">Branch: {{ acc.branch_code || 'Main Branch' }}</div>
          </q-card-section>

          <q-separator />

          <q-card-section class="bg-grey-1">
            <div class="row justify-between items-center">
              <div>
                <div class="text-caption text-grey">Available Balance</div>
                <div class="text-h5 text-weight-bolder text-deep-purple-9">
                  ₱{{ Number(acc.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
                </div>
              </div>
              <div class="text-right">
                <div class="text-caption text-grey">Ledger Balance</div>
                <div class="text-subtitle1 text-grey-8">
                  ₱{{ Number(acc.ledger_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div v-if="myAccounts.length === 0 && !loading" class="col-12 text-center q-pa-xl text-grey">
        <q-icon name="account_balance_wallet" size="64px" class="q-mb-sm text-grey-5" />
        <div class="text-subtitle1">No accounts found</div>
        <div class="text-caption">Please visit a branch or contact staff to open your first bank account.</div>
      </div>
    </div>

    <!-- Transfer Dialog -->
    <q-dialog v-model="transferDialogOpen" persistent>
      <q-card style="width: 480px; max-width: 95vw">
        <q-card-section class="bg-deep-purple-8 text-white">
          <div class="text-h6">Transfer Funds</div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-form @submit.prevent="executeTransfer" class="q-gutter-sm">
            <q-select
              v-model="transferForm.source_account_id"
              :options="sourceAccountOptions"
              label="From My Account"
              outlined
              dense
              emit-value
              map-options
              :rules="[v => !!v || 'Please select source account']"
            />

            <q-input
              v-model.number="transferForm.destination_account_id"
              label="Destination Account ID"
              type="number"
              outlined
              dense
              hint="Enter the account ID you wish to send funds to"
              :rules="[v => !!v || 'Required']"
            />

            <q-input
              v-model.number="transferForm.amount"
              label="Amount"
              type="number"
              prefix="₱"
              outlined
              dense
              :rules="[v => v > 0 || 'Amount must be greater than 0']"
            />

            <q-input
              v-model="transferForm.remarks"
              label="Remarks / Note (Optional)"
              outlined
              dense
              type="textarea"
              autogrow
            />

            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn flat label="Cancel" @click="transferDialogOpen = false" />
              <q-btn
                type="submit"
                color="deep-purple-8"
                label="Confirm Transfer"
                :loading="transferring"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '../../api'

const $q = useQuasar()
const myAccounts = ref([])
const loading = ref(false)
const transferring = ref(false)
const transferDialogOpen = ref(false)

const transferForm = ref({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: '',
  amount: null,
  transfer_type: 'INTERNAL',
  remarks: '',
})

const sourceAccountOptions = computed(() => {
  return myAccounts.value.map(acc => ({
    label: `${acc.account_number} (₱${Number(acc.available_balance).toLocaleString('en-PH', { minimumFractionDigits: 2 })})`,
    value: acc.id,
  }))
})

async function fetchAccounts() {
  loading.value = true
  try {
    const { data } = await api.get('/accounts/my')
    myAccounts.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load accounts',
    })
  } finally {
    loading.value = false
  }
}

function openTransferDialog() {
  transferForm.value = {
    source_account_id: myAccounts.value[0]?.id || null,
    destination_account_id: null,
    transfer_reference: 'TRF-' + Date.now(),
    amount: null,
    transfer_type: 'INTERNAL',
    remarks: '',
  }
  transferDialogOpen.value = true
}

async function executeTransfer() {
  transferring.value = true
  try {
    await api.post('/transfers/', transferForm.value)
    $q.notify({
      type: 'positive',
      message: 'Transfer completed successfully!',
    })
    transferDialogOpen.value = false
    await fetchAccounts()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Transfer failed. Check balance or destination account.',
    })
  } finally {
    transferring.value = false
  }
}

onMounted(fetchAccounts)
</script>

<style scoped>
.account-card {
  border-radius: 10px;
  overflow: hidden;
}
.text-mono {
  font-family: monospace;
}
</style>
