<template>
  <q-page class="q-pa-md">
    <div class="row items-center justify-between q-mb-md">
      <div>
        <div class="text-h5 text-weight-bold">System Roles</div>
        <div class="text-caption text-grey-7">Manage system access roles and descriptions</div>
      </div>
      <q-btn color="primary" icon="add" label="New Role" unelevated @click="openCreate" />
    </div>

    <q-card bordered flat>
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="id"
        :loading="loading"
        flat
        no-data-label="No roles found"
      >
        <template #body-cell-actions="props">
          <q-td :props="props" class="q-gutter-xs">
            <q-btn flat round dense icon="edit" color="primary" @click="openEdit(props.row)" />
            <q-btn flat round dense icon="delete" color="negative" @click="removeRow(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ editingId ? 'Edit Role' : 'Create Role' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-form @submit="save">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.role_code"
              label="Role Code *"
              filled
              :disable="!!editingId"
              :rules="[val => !!val || 'Role code is required']"
            />
            <q-input
              v-model="form.role_name"
              label="Role Name *"
              filled
              :rules="[val => !!val || 'Role name is required']"
            />
            <q-input
              v-model="form.description"
              label="Description"
              type="textarea"
              filled
              rows="3"
            />
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
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const form = ref({
  role_code: '',
  role_name: '',
  description: '',
})

const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'role_code', label: 'Role Code', field: 'role_code', sortable: true, align: 'left' },
  { name: 'role_name', label: 'Role Name', field: 'role_name', sortable: true, align: 'left' },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
  { name: 'created_at', label: 'Created At', field: 'created_at', format: val => val ? new Date(val).toLocaleString() : '', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/roles/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load roles' })
  } finally {
    loading.value = false
  }
}

function openCreate () {
  editingId.value = null
  form.value = { role_code: '', role_name: '', description: '' }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    role_code: row.role_code,
    role_name: row.role_name,
    description: row.description || '',
  }
  showDialog.value = true
}

async function save () {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/roles/${editingId.value}`, form.value)
      $q.notify({ type: 'positive', message: 'Role updated successfully' })
    } else {
      await api.post('/roles/', form.value)
      $q.notify({ type: 'positive', message: 'Role created successfully' })
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
    message: `Delete role "${row.role_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/roles/${row.id}`)
      $q.notify({ type: 'positive', message: 'Role deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(loadRows)
</script>
