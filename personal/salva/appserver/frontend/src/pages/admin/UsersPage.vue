<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">User Management</div>
        <div class="text-caption text-grey-7">Manage administrative, staff, and customer user accounts</div>
      </div>
      <q-btn color="primary" icon="add" label="New User" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No users found"
      >
        <template #body-cell-role_id="props">
          <q-td :props="props">
            <q-chip dense :color="getRoleColor(props.row.role_id)" text-color="white">
              {{ roleNameById[props.row.role_id] || `Role #${props.row.role_id}` }}
            </q-chip>
          </q-td>
        </template>
        <template #body-cell-account_status="props">
          <q-td :props="props">
            <q-badge :color="props.row.account_status === 'ACTIVE' ? 'positive' : 'negative'">
              {{ props.row.account_status }}
            </q-badge>
          </q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props" class="q-gutter-xs">
            <q-btn flat round dense icon="edit" color="primary" @click="openEdit(props.row)" />
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 480px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit User' : 'Create User' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.username"
                  label="Username *"
                  filled
                  :rules="[val => !!val || 'Username is required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.password"
                  label="Password *"
                  type="password"
                  filled
                  :rules="[val => !!val || 'Password is required']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.first_name"
                  label="First Name *"
                  filled
                  :rules="[val => !!val || 'First name is required']"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.last_name"
                  label="Last Name *"
                  filled
                  :rules="[val => !!val || 'Last name is required']"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.email"
                  label="Email"
                  type="email"
                  filled
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.mobile_number"
                  label="Mobile Number"
                  filled
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-select
                  v-model="form.role_id"
                  :options="roleOptions"
                  label="Role *"
                  filled
                  emit-value
                  map-options
                  :rules="[val => !!val || 'Role is required']"
                />
              </div>
              <div class="col-6">
                <q-select
                  v-model="form.account_status"
                  :options="['ACTIVE', 'LOCKED', 'DISABLED']"
                  label="Account Status *"
                  filled
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn type="submit" color="primary" :label="editingId ? 'Update' : 'Create'" :loading="saving" unelevated />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const rows = ref([])
const roleOptions = ref([])
const roleNameById = ref({})
const roleCodeById = ref({})
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  username: '',
  password: '',
  first_name: '',
  last_name: '',
  email: '',
  mobile_number: '',
  role_id: null,
  account_status: 'ACTIVE',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'username', label: 'Username', field: 'username', sortable: true, align: 'left' },
  { name: 'name', label: 'Full Name', field: row => `${row.first_name} ${row.last_name}`, align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'mobile_number', label: 'Mobile', field: 'mobile_number', align: 'left' },
  { name: 'role_id', label: 'Role', field: 'role_id', align: 'center' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

function getRoleColor (roleId) {
  const code = roleCodeById.value[roleId]
  if (code === 'ADMIN') return 'purple'
  if (code === 'STAFF') return 'blue-8'
  return 'teal'
}

async function loadRoles () {
  try {
    const { data } = await api.get('/roles/')
    roleOptions.value = data.map(r => ({ label: `${r.role_name} (${r.role_code})`, value: r.id }))
    const nameMap = {}
    const codeMap = {}
    data.forEach(r => {
      nameMap[r.id] = r.role_name
      codeMap[r.id] = r.role_code
    })
    roleNameById.value = nameMap
    roleCodeById.value = codeMap
  } catch (err) {
    console.error('Failed to load roles for user form', err)
  }
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/users/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load users' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = {
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    email: '',
    mobile_number: '',
    role_id: roleOptions.value[0]?.value || null,
    account_status: 'ACTIVE',
  }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    username: row.username,
    password: '',
    first_name: row.first_name,
    last_name: row.last_name,
    email: row.email || '',
    mobile_number: row.mobile_number || '',
    role_id: row.role_id,
    account_status: row.account_status || 'ACTIVE',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/users/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'User updated successfully' })
    } else {
      await api.post('/users/', form.value)
      $q.notify({ type: 'positive', message: 'User created successfully' })
    }
    showDialog.value = false
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete user "${row.username}" (${row.first_name} ${row.last_name})?`,
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

onMounted(async () => {
  await loadRoles()
  await loadRows()
})
</script>
