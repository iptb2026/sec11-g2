<template>
  <q-page class="customer-flow-page transfer-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow">Customer banking</div>
        <h1 class="page-title">Send Money</h1>
        <p class="page-subtitle">Transfer money to another Bembank account.</p>
      </div>
    </div>

    <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 q-mb-md">{{ errorMessage }}</q-banner>

    <MobileTransferFlow v-model="form" :accounts="accountOptions" :recipients="recipients" :recent="recentRecipients" :loading="loading" :busy="submitting" @review="reviewTransfer" @scan="scannerOpen = true" />
    <div class="customer-workspace-grid desktop-transfer-workspace">
      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="swap_horiz" size="19px" /></div>
          <div>
            <h2 class="section-heading">Transfer details</h2>
            <p class="customer-panel-subtitle">Funds move immediately between active accounts.</p>
          </div>
        </div>

        <div class="row q-gutter-sm q-mb-md"><q-btn outline icon="qr_code_scanner" label="Scan QR" @click="scannerOpen = true" /><q-btn flat icon="qr_code_2" label="Receive" to="/my-account" /></div>
        <q-input v-if="recipients.length || recentRecipients.length" v-model="recipientSearch" filled label="Search saved or recent recipients" class="q-mb-md" clearable />
        <div v-if="filteredRecent.length" class="q-mb-md"><div class="page-subtitle q-mb-sm">Recent recipients</div><q-chip v-for="person in filteredRecent" :key="person.account_number" clickable @click="form.destination_account_number = person.account_number">{{ person.name }} · {{ person.account_number }}</q-chip></div>
        <q-form ref="transferForm" class="customer-form" @submit.prevent="reviewTransfer">
          <search-select v-if="recipients.length" filled label="Choose a saved recipient" :options="filteredRecipients.map(r => ({ label: `${r.name} · ${r.account_number}`, value: r.account_number }))" emit-value map-options v-model="form.destination_account_number" />
          <search-select
            v-model="form.source_account_id"
            label="From account"
            filled
            emit-value
            map-options
            :options="accountOptions"
            :disable="loading || accountOptions.length === 0"
            :rules="[(value) => value !== null || 'Choose a source account']"
          />
          <q-input
            v-model.trim="form.destination_account_number"
            label="To account number"
            autocomplete="off"
            filled
            :rules="[(value) => !!value || 'Destination account is required']"
          />
          <q-input
            v-model="form.amount"
            label="Amount (PHP)"
            type="number"
            min="0.01"
            step="0.01"
            filled
            :rules="[(value) => Number(value) > 0 || 'Enter an amount greater than zero']"
          />
          <q-input v-model.trim="form.remarks" label="Note (optional)" maxlength="500" filled />
          <q-btn flat color="primary" icon="person_add" label="Save this recipient" :disable="!form.destination_account_number" @click="saveRecipient" />
          <div v-if="recipients.length" class="row q-gutter-xs"><q-chip v-for="recipient in recipients" :key="recipient.id" removable @remove="removeRecipient(recipient)">{{ recipient.name }}</q-chip></div>
          <q-banner v-if="accountOptions.length === 0 && !loading" dense class="bg-orange-1 text-dark">
            No active account is available for transfers.
          </q-banner>
          <div class="customer-form-actions">
            <q-btn
              type="submit"
              color="primary"
              unelevated
              no-caps
              icon="send"
              label="Review transfer"
              :loading="submitting"
              :disable="loading || accountOptions.length === 0"
            />
          </div>
        </q-form>
      </section>

      <section class="customer-panel">
        <div class="customer-panel-heading">
          <div class="customer-panel-icon"><q-icon name="history" size="19px" /></div>
          <div>
            <h2 class="section-heading">Recent transfers</h2>
            <p class="customer-panel-subtitle">Transfers involving your accounts.</p>
          </div>
        </div>
        <q-table
          :rows="transferRows"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          :pagination="{ rowsPerPage: 6, sortBy: 'created_at', descending: true }"
          no-data-label="No transfers yet"
        >
          <template #body-cell-amount="props">
            <q-td :props="props" class="text-weight-bold">PHP {{ format(props.row.amount) }}</q-td>
          </template>
          <template #body-cell-status="props">
            <q-td :props="props"><q-badge color="positive">{{ props.row.status }}</q-badge></q-td>
          </template>
        </q-table>
      </section>
    </div>
    <q-dialog v-model="confirmOpen" persistent :maximized="$q.screen.width <= 700"><q-card class="transfer-confirm-dialog mobile-flow-dialog" style="width:440px;max-width:95vw"><q-card-section><h2 class="section-heading text-center">Confirm Transfer</h2><div class="recipient-summary"><q-avatar class="recipient-avatar" icon="person_outline" /><div><strong>{{ recipientName }}</strong><small>Bembank · {{ form.destination_account_number }}</small></div></div><div class="goal-amount">₱ {{ format(form.amount) }}</div><dl class="transfer-summary"><div><dt>From account</dt><dd>{{ accountNumberById[form.source_account_id] }}</dd></div><div><dt>Transfer Fee</dt><dd>Free</dd></div><div><dt>Total Amount</dt><dd>₱ {{ format(form.amount) }}</dd></div><div v-if="form.remarks"><dt>Note</dt><dd>{{ form.remarks }}</dd></div></dl><q-banner class="customer-disclosure"><template #avatar><q-icon name="info_outline" /></template>Please review the details before confirming.</q-banner></q-card-section><q-card-actions align="right"><q-btn flat label="Go back" :disable="submitting" v-close-popup /><q-btn color="primary" label="Confirm transfer" :loading="submitting" @click="sendTransfer" /></q-card-actions></q-card></q-dialog>
    <QrScanner v-model="scannerOpen" @scanned="applyQr" />
    <q-dialog v-model="successOpen" persistent :maximized="$q.screen.width <= 700"><q-card style="width:440px;max-width:95vw"><q-card-section v-if="completed" class="text-center"><q-icon name="check_circle" color="positive" size="64px" /><h2 class="section-heading">Transfer successful!</h2><div class="goal-amount">₱ {{ format(completed.amount) }}</div><p>Sent to {{ completed.recipient }}<br>{{ completed.destination }}</p><p class="page-subtitle">{{ completed.reference }}<br>{{ new Date(completed.date).toLocaleString() }}</p><p v-if="completed.note">{{ completed.note }}</p></q-card-section><q-card-actions align="center"><q-btn outline label="View receipt" @click="receiptOpen = true" /><q-btn color="primary" label="Done" v-close-popup /></q-card-actions></q-card></q-dialog>
    <q-dialog v-model="receiptOpen"><q-card style="width:480px;max-width:95vw"><q-card-section><h2 class="section-heading">Transfer receipt</h2><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{{ receiptText }}</pre></q-card-section><q-card-actions align="right"><q-btn flat label="Close" v-close-popup /><q-btn color="primary" icon="download" label="Download receipt" @click="downloadReceipt" /></q-card-actions></q-card></q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref, nextTick, watch } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { useRoute, useRouter } from 'vue-router'
import QrScanner from '@/components/QrScanner.vue'
import MobileTransferFlow from '@/components/MobileTransferFlow.vue'
import { downloadText } from '@/utils/bank-qr'

const $q = useQuasar(), route = useRoute(), router = useRouter()
const scannerOpen = ref(false), transferForm = ref(null), recipientSearch = ref(''), recentRecipients = ref([]), recipientName = ref(''), successOpen = ref(false), receiptOpen = ref(false), completed = ref(null)
const matches = r => `${r.name} ${r.account_number}`.toLowerCase().includes((recipientSearch.value || '').toLowerCase())
const filteredRecipients = computed(() => recipients.value.filter(matches))
const filteredRecent = computed(() => recentRecipients.value.filter(matches))
const receiptText = computed(() => completed.value ? `BEMBANK — TRANSFER RECEIPT\n\nReference: ${completed.value.reference}\nDate: ${completed.value.date}\nFrom: ${completed.value.source}\nTo: ${completed.value.recipient} · ${completed.value.destination}\nAmount: PHP ${format(completed.value.amount)}\nFee: Free\nNote: ${completed.value.note || '—'}\nStatus: SUCCESS\n\nSimulated banking transaction.` : '')
function downloadReceipt () { downloadText(receiptText.value, `bembank-${completed.value.reference}.txt`) }
function applyQr (data) { form.value.destination_account_number = data.account_number; form.value.amount = data.amount || null; $q.notify({ message: 'QR details filled in. Review the recipient before sending.' }) }
async function reviewTransfer () { if (submitting.value) return; submitting.value = true; errorMessage.value = ''; try { recipientName.value = (await api.post('/customer/recipient-lookup', { account_number: form.value.destination_account_number })).data.name; confirmOpen.value = true } catch (e) { errorMessage.value = e.response?.data?.detail || 'Could not verify recipient.' } finally { submitting.value = false } }
const accounts = ref([])
const transferRows = ref([])
const loading = ref(true)
const submitting = ref(false)
const confirmOpen = ref(false)
const recipients = ref([])
function saveRecipient () { $q.dialog({ title: 'Save recipient', prompt: { model: '', label: 'Recipient nickname', isValid: value => !!value.trim() && value.length <= 80 }, cancel: true }).onOk(async name => { try { await api.post('/customer/recipients/', { name, account_number: form.value.destination_account_number }); recipients.value = (await api.get('/customer/recipients/')).data } catch (e) { $q.notify({ type: 'negative', message: e.response?.data?.detail || 'Could not save recipient' }) } }) }
async function removeRecipient (recipient) { try { await api.delete(`/customer/recipients/${recipient.id}`); recipients.value = recipients.value.filter(r => r.id !== recipient.id) } catch { $q.notify({ type: 'negative', message: 'Could not remove recipient' }) } }
const errorMessage = ref('')
const form = ref({ source_account_id: null, destination_account_number: '', amount: null, remarks: '' })
const activeAccounts = computed(() => accounts.value.filter((account) => account.status === 'ACTIVE'))
const accountOptions = computed(() => activeAccounts.value.map((account) => ({
  label: `${account.account_number} · PHP ${format(account.available_balance)}`,
  value: account.id,
})))
const accountNumberById = computed(() => Object.fromEntries(accounts.value.map((account) => [account.id, account.account_number])))
const columns = [
  { name: 'created_at', label: 'Date', field: 'created_at', align: 'left', sortable: true },
  { name: 'route', label: 'Route', field: (row) => `${accountNumberById.value[row.source_account_id] || 'Account'} → ${accountNumberById.value[row.destination_account_id] || 'External account'}`, align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
]

function format (value) {
  return Number(value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData () {
  loading.value = true
  errorMessage.value = ''
  try {
    const [accountResponse, transferResponse, recipientResponse, recentResponse] = await Promise.all([
      api.get('/customer/accounts/'),
      api.get('/customer/transfers/'),
      api.get('/customer/recipients/'),
      api.get('/customer/recent-recipients/'),
    ])
    accounts.value = accountResponse.data
    transferRows.value = transferResponse.data
    recipients.value = recipientResponse.data
    recentRecipients.value = recentResponse.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Could not load transfer data.'
  } finally {
    loading.value = false
  }
}

async function sendTransfer () {
  if (submitting.value) return
  submitting.value = true
  try {
    const { data } = await api.post('/customer/transfers/', form.value)
    completed.value = { reference: data.transfer_reference, date: data.completed_at || data.created_at, amount: data.amount, recipient: recipientName.value, source: accountNumberById.value[form.value.source_account_id], destination: form.value.destination_account_number, note: form.value.remarks }
    successOpen.value = true
    confirmOpen.value = false
    form.value = { source_account_id: null, destination_account_number: '', amount: null, remarks: '' }
    await nextTick(); transferForm.value?.resetValidation()
    $q.notify({ type: 'positive', message: 'Transfer completed' })
    await loadData()
  } catch (error) {
    $q.notify({ type: 'negative', message: error.response?.data?.detail || 'Transfer could not be completed.' })
  } finally {
    submitting.value = false
  }
}

watch(() => route.query.scan, (scan) => { if (scan === '1') scannerOpen.value = true }, { immediate: true })
watch(scannerOpen, (open) => { if (!open && route.query.scan === '1') { const query = { ...route.query }; delete query.scan; router.replace({ query }) } })
onMounted(loadData)
</script>
