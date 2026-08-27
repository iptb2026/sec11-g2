<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Roles</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add Role" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn flat dense icon="edit" color="primary" @click="openEdit(props.row)" size="sm" />
          <q-btn flat dense icon="delete" color="negative" @click="confirmDelete(props.row)" size="sm" />
        </q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 450px; max-width: 95vw">
        <q-card-section><div class="text-h6">{{ editMode ? 'Edit Role' : 'Create Role' }}</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.role_code" label="Role Code" outlined dense :rules="[v => !!v || 'Required']" />
            <q-input v-model="form.role_name" label="Role Name" outlined dense :rules="[v => !!v || 'Required']" />
            <q-input v-model="form.description" label="Description" outlined dense type="textarea" autogrow />
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
const rows = ref([]), loading = ref(false), saving = ref(false), dialogOpen = ref(false), editMode = ref(false), editId = ref(null)
const columns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
  { name: 'role_code', label: 'Code', field: 'role_code', align: 'left' },
  { name: 'role_name', label: 'Name', field: 'role_name', align: 'left' },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]
const emptyForm = () => ({ role_code: '', role_name: '', description: '' })
const form = ref(emptyForm())
async function fetchData() { loading.value = true; try { rows.value = (await api.get('/roles/')).data } catch(e) { $q.notify({type:'negative',message:'Failed to load'}) } finally { loading.value = false } }
function openCreate() { form.value = emptyForm(); editMode.value = false; dialogOpen.value = true }
function openEdit(row) { form.value = { ...row }; editId.value = row.id; editMode.value = true; dialogOpen.value = true }
async function save() { saving.value = true; try { if (editMode.value) { await api.put(`/roles/${editId.value}`, form.value); $q.notify({type:'positive',message:'Updated'}) } else { await api.post('/roles/', form.value); $q.notify({type:'positive',message:'Created'}) }; dialogOpen.value = false; await fetchData() } catch(e) { $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value = false } }
function confirmDelete(row) { $q.dialog({title:'Delete Role',message:`Delete "${row.role_name}"?`,cancel:true,persistent:true}).onOk(async () => { try { await api.delete(`/roles/${row.id}`); $q.notify({type:'positive',message:'Deleted'}); await fetchData() } catch(e) { $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } }) }
onMounted(fetchData)
</script>
