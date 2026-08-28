<template>
  <q-page class="admin-page q-pa-md q-pa-lg-xl">
    <div class="admin-shell">
      <div class="page-heading">
        <div><p class="eyebrow">ADMINISTRATION</p><h1>User management</h1><p>Create, edit, disable, and remove banking users.</p></div>
        <q-btn color="primary" unelevated no-caps icon="person_add" label="Add user" @click="openCreate" />
      </div>

      <q-banner v-if="message" rounded :class="{ 'error-banner': error, 'success-banner': !error }" class="q-mb-md">
        <template #avatar><q-icon :name="error ? 'error_outline' : 'task_alt'" /></template>{{ message }}
      </q-banner>

      <q-table flat bordered row-key="id" :rows="users" :columns="columns" :loading="loading" class="user-table" no-data-label="No users found">
        <template #body-cell-role="props"><q-td :props="props"><q-badge color="secondary" :label="roleName(props.row.role_id)" /></q-td></template>
        <template #body-cell-status="props"><q-td :props="props"><q-badge :color="props.row.account_status === 'ACTIVE' ? 'positive' : 'negative'" :label="props.row.account_status" /></q-td></template>
        <template #body-cell-actions="props">
          <q-td :props="props" class="actions-cell">
            <q-btn flat round dense icon="edit" aria-label="Edit user" @click="openEdit(props.row)"><q-tooltip>Edit user</q-tooltip></q-btn>
            <q-btn flat round dense :icon="props.row.account_status === 'ACTIVE' ? 'person_off' : 'person'" :aria-label="props.row.account_status === 'ACTIVE' ? 'Disable user' : 'Enable user'" @click="toggleStatus(props.row)"><q-tooltip>{{ props.row.account_status === 'ACTIVE' ? 'Disable user' : 'Enable user' }}</q-tooltip></q-btn>
            <q-btn flat round dense color="negative" icon="delete" aria-label="Delete user" :disable="props.row.id === authStore.userId" @click="removeUser(props.row)"><q-tooltip>Delete user</q-tooltip></q-btn>
          </q-td>
        </template>
      </q-table>
    </div>

    <q-dialog v-model="dialogOpen">
      <q-card class="user-dialog">
        <q-card-section><div class="text-h6">{{ editing ? 'Edit user' : 'Create user' }}</div><div class="text-caption text-grey-7">Admin-only account management</div></q-card-section>
        <q-card-section>
          <q-form class="q-gutter-md" @submit.prevent="saveUser">
            <q-input v-model.trim="form.username" outlined label="Username" :disable="editing" :rules="[required]" />
            <div class="form-row"><q-input v-model.trim="form.first_name" outlined label="First name" :rules="[required]" /><q-input v-model.trim="form.last_name" outlined label="Last name" :rules="[required]" /></div>
            <q-input v-model.trim="form.email" outlined type="email" label="Email" :rules="[validEmail]" />
            <q-input v-model="form.password" outlined type="password" :label="editing ? 'New password (optional)' : 'Password'" :rules="[editing ? () => true : required]" />
            <div class="form-row"><q-select v-model="form.role_id" outlined emit-value map-options label="Role" :options="roleOptions" /><q-select v-model="form.account_status" outlined emit-value map-options label="Status" :options="statusOptions" /></div>
            <div class="dialog-actions"><q-btn flat no-caps label="Cancel" @click="dialogOpen = false" /><q-btn color="primary" unelevated no-caps type="submit" :loading="saving" :label="editing ? 'Save changes' : 'Create user'" /></div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const authStore = useAuthStore()
const users = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const editing = ref(false)
const message = ref('')
const error = ref(false)
const form = ref({ username: '', first_name: '', last_name: '', email: '', password: '', role_id: 3, account_status: 'ACTIVE' })
const roles = [{ id: 1, name: 'ADMIN' }, { id: 2, name: 'STAFF' }, { id: 3, name: 'CUSTOMER' }, { id: 5, name: 'AUDITOR' }, { id: 6, name: 'MANAGER' }]
const roleOptions = roles.map((role) => ({ label: role.name, value: role.id }))
const statusOptions = [{ label: 'Active', value: 'ACTIVE' }, { label: 'Locked', value: 'LOCKED' }, { label: 'Disabled', value: 'DISABLED' }]
const columns = [{ name: 'username', label: 'Username', field: 'username', align: 'left' }, { name: 'name', label: 'Name', field: (row) => `${row.first_name} ${row.last_name}`, align: 'left' }, { name: 'role', label: 'Role', field: 'role_id' }, { name: 'status', label: 'Status', field: 'account_status' }, { name: 'actions', label: 'Actions', field: 'actions', align: 'right' }]

const required = (value) => !!value || 'Required'
const validEmail = (value) => !value || /.+@.+\..+/.test(value) || 'Enter a valid email'
function roleName (id) { return roles.find((role) => role.id === id)?.name || `ROLE ${id}` }
async function loadUsers () { loading.value = true; try { const { data } = await api.get('/users/'); users.value = data } catch (requestError) { showError(requestError) } finally { loading.value = false } }
function resetForm () { form.value = { username: '', first_name: '', last_name: '', email: '', password: '', role_id: 3, account_status: 'ACTIVE' } }
function openCreate () { editing.value = false; resetForm(); dialogOpen.value = true }
function openEdit (user) { editing.value = true; form.value = { username: user.username, first_name: user.first_name, last_name: user.last_name, email: user.email || '', password: '', role_id: user.role_id, account_status: user.account_status, id: user.id }; dialogOpen.value = true }
async function saveUser () { saving.value = true; clearMessage(); try { const payload = { ...form.value }; if (!payload.password) delete payload.password; if (editing.value) await api.put(`/users/${form.value.id}`, payload); else await api.post('/users/', payload); dialogOpen.value = false; showSuccess(editing.value ? 'User updated.' : 'User created.'); await loadUsers() } catch (requestError) { showError(requestError) } finally { saving.value = false } }
async function toggleStatus (user) { try { await api.put(`/users/${user.id}`, { username: user.username, first_name: user.first_name, last_name: user.last_name, email: user.email, role_id: user.role_id, account_status: user.account_status === 'ACTIVE' ? 'DISABLED' : 'ACTIVE' }); showSuccess(`User ${user.account_status === 'ACTIVE' ? 'disabled' : 'enabled'}.`); await loadUsers() } catch (requestError) { showError(requestError) } }
async function removeUser (user) { if (!window.confirm(`Delete user ${user.username}? This cannot be undone.`)) return; try { await api.delete(`/users/${user.id}`); showSuccess('User deleted.'); await loadUsers() } catch (requestError) { showError(requestError) } }
function clearMessage () { message.value = ''; error.value = false }
function showSuccess (text) { message.value = text; error.value = false }
function showError (requestError) { message.value = requestError.response?.data?.detail || 'Admin operation failed.'; error.value = true }
onMounted(loadUsers)
</script>

<style scoped>
.admin-page { background: #f4f7f6; color: #182827; }.admin-shell { max-width: 1180px; margin: 0 auto; }.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin: 28px 0 24px; }.eyebrow { margin: 0 0 8px; color: #53746d; font-size: 11px; font-weight: 800; letter-spacing: 1.6px; }h1 { margin: 0 0 8px; font-size: 2.4rem; line-height: 1; }.page-heading p:last-child { margin: 0; color: #71817d; }.user-table { border-radius: 10px; background: #fff; }.success-banner { color: #176653; background: #d7eee5; }.error-banner { color: #9e3737; background: #fff0ef; }.actions-cell { white-space: nowrap; }.user-dialog { width: min(100%, 560px); }.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }.dialog-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px; }@media (max-width: 600px) { .page-heading { align-items: stretch; flex-direction: column; }.form-row { grid-template-columns: 1fr; gap: 0; } }
</style>
