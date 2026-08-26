<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Deposits</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Deposit' : 'New Deposit' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-select
            v-model="form.account_id"
            label="Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.holder }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <q-input
            v-if="form.account_id"
            :model-value="accountHolderName"
            label="Account Holder"
            filled
            readonly
          />
          <q-input v-model="form.reference_number" label="Reference Number" filled />
          <q-input v-model.number="form.amount" label="Amount" type="number" filled />
          <q-select
            v-model="form.deposit_channel"
            label="Channel"
            filled
            use-input
            hide-selected
            fill-input
            input-debounce="0"
            new-value-mode="add-unique"
            :options="filteredChannelOptions"
            @filter="filterChannelOptions"
            hint="e.g. ONLINE, ATM, TELLER"
          />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Auto ID', field: 'account_id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: (row) => accountNumberByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'account_name', label: 'Account Name', field: (row) => accountHolderByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel', align: 'left' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({ account_id: null, reference_number: '', amount: 0, deposit_channel: '', remarks: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

const channelOptions = ['ONLINE', 'ATM', 'TELLER']
const filteredChannelOptions = ref(channelOptions)
function filterChannelOptions (val, update) {
  update(() => {
    if (val === '') {
      filteredChannelOptions.value = channelOptions
    } else {
      const needle = val.toLowerCase()
      filteredChannelOptions.value = channelOptions.filter((v) => v.toLowerCase().includes(needle))
    }
  })
}

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/deposits/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }] = await Promise.all([
    api.get('/accounts/'),
    api.get('/users/'),
  ])

  const nameByUserId = {}
  users.forEach((u) => {
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`
  })

  accountOptions.value = accounts.map((a) => ({
    label: a.account_number,
    value: a.id,
    holder: nameByUserId[a.customer_id] || '',
  }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    deposit_channel: row.deposit_channel,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/deposits/${editingId.value}`, form.value)
    } else {
      await api.post('/deposits/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Deposit saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete deposit "${row.reference_number}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/deposits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Deposit deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
