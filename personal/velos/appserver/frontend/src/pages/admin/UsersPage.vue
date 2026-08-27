<template>
  <q-page padding>
    <div class="row items-center justify-between">
      <div>
        <div class="text-h5">User Management</div>
        <div class="text-subtitle2">Manage application users</div>
      </div>
      <div>
        <q-btn color="primary" label="Add User" @click="openDialog()" />
        <q-btn outline class="q-ml-sm" color="secondary" label="Export CSV" @click="exportCsv" />
      </div>
    </div>

    <q-card class="q-mt-md">
      <q-card-section>
        <q-table :rows="users" :columns="cols" row-key="id" :loading="loading">
          <template v-slot:body-cell-actions="props">
            <q-td align="left">
              <q-btn dense flat icon="edit" @click="openDialog(props.row)" />
              <q-btn dense flat :icon="props.row.is_active ? 'block' : 'check'" @click="toggleActive(props.row)" />
              <q-btn dense flat icon="delete" color="negative" @click="confirmDelete(props.row)" />
            </q-td>
          </template>
          <template v-slot:no-data>
            <EmptyState title="No users" description="No users match your filters." />
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <q-dialog v-model="dialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ editId ? 'Edit' : 'Add' }} User</div>
        </q-card-section>

        <q-card-section>
          <q-input v-model="form.full_name" label="Full name" />
          <q-input v-model="form.email" label="Email" />
          <q-select v-model="form.role_code" :options="roles" label="Role" />
          <q-toggle v-model="form.is_active" label="Active" />
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
import { ref, onMounted } from 'vue'
import * as userService from '@/services/userService'
import notificationService from '@/services/notificationService'
import { useQuasar } from 'quasar'
import EmptyState from '@/components/EmptyState.vue'

const $q = useQuasar()
const users = ref([])
const loading = ref(false)
const dialog = ref(false)
const editId = ref(null)
const form = ref({ full_name: '', email: '', role_code: 'customer', is_active: true })
const roles = ['admin','staff','customer']

const cols = [
  { name: 'full_name', label: 'Name', field: 'full_name' },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'role_code', label: 'Role', field: 'role_code' },
  { name: 'is_active', label: 'Status', field: 'is_active' },
  { name: 'actions', label: 'Actions', field: 'id' }
]

async function load() {
  loading.value = true
  try {
    users.value = await userService.listUsers()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load users' })
  } finally { loading.value = false }
}

function openDialog(u) {
  if (u) {
    editId.value = u.id
    form.value = { full_name: u.full_name, email: u.email, role_code: u.role_code, is_active: u.is_active }
  } else {
    editId.value = null
    form.value = { full_name: '', email: '', role_code: 'customer', is_active: true }
  }
  dialog.value = true
}

async function save() {
  try {
    if (editId.value) {
      await userService.updateUser(editId.value, form.value)
      $q.notify({ type: 'positive', message: 'User updated' })
      notificationService.add('User updated', `${form.value.full_name} was updated by admin.`)
    } else {
      await userService.createUser({ ...form.value, password: 'password123' })
      $q.notify({ type: 'positive', message: 'User created' })
      notificationService.add('New user', `${form.value.full_name} (${form.value.role_code}) created`)
    }
    dialog.value = false
    await load()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Save failed' })
  }
}

async function confirmDelete(row) {
  const ok = await $q.dialog({ title: 'Confirm delete', message: `Delete ${row.full_name}? This action cannot be undone.`, cancel: true, persistent: true })
  if (ok === true) return deleteUser(row)
}

async function deleteUser(row) {
  try {
    await userService.deleteUser(row.id)
    $q.notify({ type: 'positive', message: 'User deleted' })
    notificationService.add('User deleted', `${row.full_name} was deleted`)
    await load()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Delete failed' })
  }
}

async function toggleActive(row) {
  try {
    if (row.is_active) {
      await userService.deactivateUser(row.id)
      notificationService.add('User deactivated', `${row.full_name} was deactivated`)
      $q.notify({ type: 'info', message: 'User deactivated' })
    } else {
      await userService.activateUser(row.id)
      notificationService.add('User activated', `${row.full_name} was activated`)
      $q.notify({ type: 'positive', message: 'User activated' })
    }
    await load()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Operation failed' })
  }
}

onMounted(load)

function exportCsv() {
  const header = ['Name','Email','Role','Status','Registered']
  const rows = users.value.map(u => [u.full_name, u.email, u.role_code, u.is_active ? 'Active' : 'Inactive', u.created_at])
  const csv = [header, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'users.csv'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
</script>
