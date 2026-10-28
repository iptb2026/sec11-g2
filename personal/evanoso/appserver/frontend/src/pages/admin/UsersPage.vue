<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Users</div>
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
      <q-card style="width: 460px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit User' : 'New User' }}</div>
        </q-card-section>

        <q-form @submit="save">
        <q-card-section class="q-gutter-md">
          <q-input v-model.trim="form.username" label="Username" filled :rules="[required, validUsername]" />
          <NewPasswordField v-if="!editingId" v-model="form.password" label="Initial password" />
          <q-input v-model.trim="form.email" label="Email (optional)" type="email" filled :rules="[validEmail]" />
          <q-input v-model="form.mobile_number" label="Mobile Number" filled />
          <q-input v-model.trim="form.first_name" label="First Name" filled :rules="[required]" />
          <q-input v-model.trim="form.middle_name" label="Middle Name (optional)" filled />
          <q-input v-model.trim="form.last_name" label="Last Name" filled :rules="[required]" />
          <DatePickerField v-model="form.date_of_birth" label="Date of Birth" filled clearable />
          <q-select
            v-model="form.role_id"
            label="Role"
            filled
            emit-value
            map-options
            :options="roleOptions"
            :rules="[required]"
          />
          <q-select
            v-if="editingId"
            v-model="form.account_status"
            label="Account access"
            filled
            emit-value
            map-options
            :options="statusOptions"
            hint="Locked is temporary; Disabled blocks access until re-enabled."
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" type="submit" />
        </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { passwordRule } from '@/utils/password-policy'
import NewPasswordField from '@/components/NewPasswordField.vue'
import DatePickerField from '@/components/DatePickerField.vue'
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { optionLabel } from '@/utils/filter-options'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'username', label: 'Username', field: 'username', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'first_name', label: 'First Name', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Last Name', field: 'last_name', align: 'left' },
  { name: 'role_id', label: 'Role', field: row => optionLabel(roleOptions.value, row.role_id), align: 'left' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const roleOptions = ref([])
const statusOptions = [
  { label: 'Active — can sign in', value: 'ACTIVE' },
  { label: 'Locked — temporarily blocked', value: 'LOCKED' },
  { label: 'Disabled — access turned off', value: 'DISABLED' },
]
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const required = value => (value !== null && value !== undefined && String(value).trim() !== '') || 'This field is required'
const validUsername = value => /^[a-zA-Z0-9_.-]{3,100}$/.test(value) || 'Use 3–100 letters, numbers, dots, dashes, or underscores'
const validEmail = value => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Enter a valid email address'
const emptyForm = () => ({
  username: '',
  password: '',
  email: '',
  mobile_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  date_of_birth: '',
  role_id: null,
  account_status: 'ACTIVE',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/users/')
  rows.value = data
  loading.value = false
}

async function loadRoleOptions () {
  const { data } = await api.get('/roles/')
  roleOptions.value = data.map((r) => ({ label: `${r.role_code} - ${r.role_name}`, value: r.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    username: row.username,
    password: '',
    email: row.email,
    mobile_number: row.mobile_number,
    first_name: row.first_name,
    middle_name: row.middle_name,
    last_name: row.last_name,
    date_of_birth: row.date_of_birth,
    role_id: row.role_id,
    account_status: row.account_status,
  }
  showDialog.value = true
}

async function save () {
  if (!editingId.value) {
    const validation = passwordRule(form.value.password)
    if (validation !== true) { $q.notify({ type: 'negative', message: validation }); return }
  }
  try {
    if (editingId.value) {
      const user = { ...form.value }
      delete user.password
      await api.put(`/users/${editingId.value}`, user)
    } else {
      await api.post('/users/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'User saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete user "${row.username}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/users/${row.id}`)
      $q.notify({ type: 'positive', message: 'User deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadRoleOptions()
})
</script>
