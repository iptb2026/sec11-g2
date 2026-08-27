<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Users</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add User" @click="openCreate" id="add-user-btn" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense icon="edit" color="primary" @click="openEdit(props.row)" size="sm" />
          <q-btn flat dense icon="delete" color="negative" @click="confirmDelete(props.row)" size="sm" />
        </q-td>
      </template>
    </q-table>

    <!-- Create/Edit Dialog -->
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">{{ editMode ? 'Edit User' : 'Create User' }}</div>
        </q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.username" label="Username" outlined dense :rules="[r]" />
            <q-input v-model="form.password" label="Password" outlined dense type="password" :rules="[r]" />
            <q-input v-model="form.email" label="Email" outlined dense />
            <q-input v-model="form.first_name" label="First Name" outlined dense :rules="[r]" />
            <q-input v-model="form.middle_name" label="Middle Name" outlined dense />
            <q-input v-model="form.last_name" label="Last Name" outlined dense :rules="[r]" />
            <q-input v-model="form.mobile_number" label="Mobile Number" outlined dense />
            <q-select v-model="form.role_id" :options="roleOptions" label="Role" outlined dense emit-value map-options :rules="[r]" />
            <q-select v-model="form.account_status" :options="['ACTIVE','LOCKED','DISABLED']" label="Status" outlined dense />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn flat label="Cancel" @click="dialogOpen = false" />
              <q-btn type="submit" color="primary" :label="editMode ? 'Update' : 'Create'" :loading="saving" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '../../api'

const $q = useQuasar()
const rows = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editMode = ref(false)
const editId = ref(null)
const roleOptions = ref([])

const r = val => !!val || 'Required'

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'username', label: 'Username', field: 'username', sortable: true, align: 'left' },
  { name: 'first_name', label: 'First Name', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Last Name', field: 'last_name', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'role_id', label: 'Role ID', field: 'role_id', align: 'left' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const emptyForm = () => ({
  username: '', password: '', email: '', first_name: '', middle_name: '',
  last_name: '', mobile_number: '', role_id: null, account_status: 'ACTIVE', date_of_birth: null,
})
const form = ref(emptyForm())

async function fetchData() {
  loading.value = true
  try {
    const [usersRes, rolesRes] = await Promise.all([api.get('/users/'), api.get('/roles/')])
    rows.value = usersRes.data
    roleOptions.value = rolesRes.data.map(r => ({ label: `${r.role_name} (${r.role_code})`, value: r.id }))
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Failed to load users' })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value = emptyForm()
  editMode.value = false
  dialogOpen.value = true
}

function openEdit(row) {
  form.value = { ...row, password: 'placeholder' }
  editId.value = row.id
  editMode.value = true
  dialogOpen.value = true
}

async function save() {
  saving.value = true
  try {
    if (editMode.value) {
      await api.put(`/users/${editId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'User updated' })
    } else {
      await api.post('/users/', form.value)
      $q.notify({ type: 'positive', message: 'User created' })
    }
    dialogOpen.value = false
    await fetchData()
  } catch (e) {
    $q.notify({ type: 'negative', message: e.response?.data?.detail || 'Operation failed' })
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) {
  $q.dialog({
    title: 'Delete User',
    message: `Are you sure you want to delete user "${row.username}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/users/${row.id}`)
      $q.notify({ type: 'positive', message: 'User deleted' })
      await fetchData()
    } catch (e) {
      $q.notify({ type: 'negative', message: e.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(fetchData)
</script>
