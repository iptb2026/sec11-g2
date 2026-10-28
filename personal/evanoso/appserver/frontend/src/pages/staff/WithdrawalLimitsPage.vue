<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Withdrawal Limits</div>
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
          <div class="text-h6">{{ editingId ? 'Edit Withdrawal Limit' : 'New Withdrawal Limit' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <search-select
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
          </search-select>
          <q-input
            v-if="form.account_id"
            :model-value="accountHolderName"
            label="Account Holder"
            filled
            readonly
          />
          <q-input v-model.number="form.daily_limit_amount" label="Daily Limit Amount" type="number" filled />
          <DatePickerField v-model="form.last_reset_date" label="Last Reset Date" filled />
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
import DatePickerField from '@/components/DatePickerField.vue'
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { optionLabel } from '@/utils/filter-options'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account', field: row => optionLabel(accountOptions.value, row.account_id), align: 'left' },
  { name: 'daily_limit_amount', label: 'Daily Limit', field: 'daily_limit_amount', align: 'right' },
  { name: 'daily_used_amount', label: 'Used Today', field: 'daily_used_amount', align: 'right' },
  { name: 'last_reset_date', label: 'Last Reset', field: 'last_reset_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const accountHolderByAccountId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({ account_id: null, daily_limit_amount: 0, last_reset_date: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/withdrawal-limits/')
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
    daily_limit_amount: Number(row.daily_limit_amount),
    last_reset_date: row.last_reset_date,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      // account_id can't change on an existing withdrawal limit, only the limit/reset date
      await api.put(`/withdrawal-limits/${editingId.value}`, {
        daily_limit_amount: form.value.daily_limit_amount,
        last_reset_date: form.value.last_reset_date,
      })
    } else {
      await api.post('/withdrawal-limits/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Withdrawal limit saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete withdrawal limit #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/withdrawal-limits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Withdrawal limit deleted' })
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
