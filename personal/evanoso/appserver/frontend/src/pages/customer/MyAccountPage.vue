<template>
  <q-page class="customer-flow-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow">Customer banking</div>
        <h1 class="page-title">My accounts</h1>
        <p class="page-subtitle">Balances, account details, and receive codes.</p>
      </div>
    </div>

    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">
      {{ errorMessage }}
    </q-banner>

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <div v-else-if="accounts.length === 0" class="text-grey-7">
      No account is registered under your profile yet. A bank staff member can open one for you.
    </div>

    <div v-else class="customer-account-grid">
      <q-card v-for="acc in accounts" :key="acc.id" flat bordered class="customer-account-card">
        <q-card-section class="customer-account-head">
          <div>
            <div class="account-overline">BEMBANK · {{ acc.currency_code }}</div>
            <div class="customer-account-number">{{ acc.account_number }}</div>
          </div>
          <q-badge :color="acc.status === 'ACTIVE' ? 'positive' : 'grey'">{{ acc.status }}</q-badge>
        </q-card-section>
        <q-card-section class="customer-account-content">
          <div class="customer-balance-grid">
            <div>
              <div class="account-overline">Available balance</div>
              <div class="customer-balance-value">{{ acc.currency_code }} {{ format(acc.available_balance) }}</div>
            </div>
            <div>
              <div class="account-overline">Ledger balance</div>
              <div class="customer-secondary-balance">{{ acc.currency_code }} {{ format(acc.ledger_balance) }}</div>
            </div>
          </div>
          <div class="customer-account-meta">
            <span>Opened {{ acc.opened_at?.slice(0, 10) }}</span>
            <span v-if="acc.branch_code">Branch {{ acc.branch_code }}</span>
          </div>
          <div class="customer-account-actions">
            <q-btn flat no-caps icon="qr_code_2" label="Receive" @click="showReceiveCode(acc)" />
            <q-btn flat no-caps icon="swap_horiz" label="Send funds" to="/customer/transfers" />
          </div>
        </q-card-section>
      </q-card>
    </div>

    <AccountApplications />
    <q-dialog v-model="qrOpen" :maximized="$q.screen.width <= 700">
      <q-card class="receive-qr-dialog">
        <q-card-section class="receive-qr-header">
          <div>
            <div class="eyebrow">Receive funds</div>
            <div class="section-heading">My QR Code</div>
          </div>
          <q-btn flat dense round icon="close" aria-label="Close" v-close-popup />
        </q-card-section>
        <q-card-section class="receive-qr-content">
          <div class="qr-mode-tabs"><q-btn flat label="Receive" class="selected" /><q-btn flat label="Scan" to="/customer/transfers?scan=1" /></div>
          <div class="qr-paper">
          <img v-if="qrImage" :src="qrImage" alt="QR code with account details" class="receive-qr-image">
          <strong>{{ auth.fullName || auth.username }}</strong>
          <div class="receive-qr-number">{{ selectedAccount?.account_number }}</div>
          <div class="receive-qr-bank">BEMBANK · {{ selectedAccount?.currency_code }}</div>
          </div>
          <div class="qr-action-row"><q-btn flat stack icon="ios_share" label="Share" @click="shareQr" /><q-btn flat stack icon="download" label="Save" @click="saveQr" /><q-btn flat stack icon="edit_square" label="Set Amount" @click="amountOpen = !amountOpen" /></div>
          <q-form v-if="amountOpen" class="q-mt-md" @submit="setAmount"><q-input v-model="requestedAmount" filled label="Requested amount (optional)" type="number" min="0.01" step="0.01" /><q-btn flat label="Set amount" type="submit" /></q-form>
          <div v-if="qrAmount" class="q-my-sm">Requested: PHP {{ format(qrAmount) }}</div>
          <q-banner class="bank-feedback"><template #avatar><q-icon name="info_outline" /></template>Let others scan this QR code to send you money securely.</q-banner>
          <q-btn outline no-caps icon="content_copy" label="Copy account number" @click="copyAccountNumber" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { copyToClipboard, useQuasar } from 'quasar'
import QRCode from 'qrcode'
import api from '@/services/api'
import { accountQrPayload } from '@/utils/bank-qr'
import AccountApplications from '@/components/AccountApplications.vue'
import { useAuthStore } from '@/stores/auth-store'
import { useRoute } from 'vue-router'

const $q = useQuasar()
const auth = useAuthStore(), route = useRoute(), amountOpen = ref(false)
const accounts = ref([])
const loading = ref(true)
const errorMessage = ref('')
const qrOpen = ref(false)
const qrImage = ref('')
const selectedAccount = ref(null)
const requestedAmount = ref(''), qrAmount = ref('')

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function showReceiveCode (account) {
  try {
    selectedAccount.value = account
    requestedAmount.value = ''; qrAmount.value = ''
    qrImage.value = await QRCode.toDataURL(accountQrPayload(account), { width: 280, margin: 2 })
    qrOpen.value = true
  } catch {
    $q.notify({ type: 'negative', message: 'Could not generate the receive QR code' })
  }
}

async function setAmount () {
  try { const payload = accountQrPayload(selectedAccount.value, requestedAmount.value); qrImage.value = await QRCode.toDataURL(payload, { width: 280, margin: 2 }); qrAmount.value = requestedAmount.value } catch (e) { $q.notify({ type: 'negative', message: e.message || 'Enter a valid amount.' }) }
}
function saveQr () { const link = document.createElement('a'); link.href = qrImage.value; link.download = `bembank-${selectedAccount.value.account_number}.png`; link.click() }
async function shareQr () {
  try { const bytes = Uint8Array.from(atob(qrImage.value.split(',')[1]), char => char.charCodeAt(0)); const file = new File([bytes], 'bembank-receive.png', { type: 'image/png' }); if (navigator.canShare?.({ files: [file] })) await navigator.share({ title: 'Bembank receive code', files: [file] }); else { saveQr(); $q.notify({ message: 'QR image saved. Attach it in your preferred messaging app.' }) } } catch (e) { if (e.name !== 'AbortError') $q.notify({ type: 'negative', message: 'Could not share. Use Save QR instead.' }) }
}

async function copyAccountNumber () {
  try {
    await copyToClipboard(selectedAccount.value.account_number)
    $q.notify({ type: 'positive', message: 'Account number copied' })
  } catch {
    $q.notify({ type: 'negative', message: 'Could not copy account number' })
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/customer/accounts/')
    accounts.value = data
    if (route.query.receive === '1' && data.length) await showReceiveCode(data[0])
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load your accounts.'
  } finally {
    loading.value = false
  }
})
</script>
