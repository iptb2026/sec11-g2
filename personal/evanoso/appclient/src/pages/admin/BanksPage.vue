<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Banks</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add Bank" @click="openCreate" />
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
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section><div class="text-h6">{{ editMode ? 'Edit Bank' : 'Create Bank' }}</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.bank_code" label="Bank Code" outlined dense :rules="[v => !!v || 'Required']" />
            <q-input v-model="form.bank_name" label="Bank Name" outlined dense :rules="[v => !!v || 'Required']" />
            <q-input v-model="form.short_name" label="Short Name" outlined dense />
            <q-input v-model="form.swift_code" label="SWIFT Code" outlined dense />
            <q-input v-model="form.api_endpoint" label="API Endpoint" outlined dense />
            <q-input v-model="form.contact_email" label="Contact Email" outlined dense />
            <q-select v-model="form.status" :options="['ACTIVE','INACTIVE']" label="Status" outlined dense />
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
  { name: 'bank_code', label: 'Code', field: 'bank_code', align: 'left' },
  { name: 'bank_name', label: 'Name', field: 'bank_name', align: 'left' },
  { name: 'short_name', label: 'Short', field: 'short_name', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]
const emptyForm = () => ({ bank_code:'', bank_name:'', short_name:'', swift_code:'', api_endpoint:'', contact_email:'', status:'ACTIVE' })
const form = ref(emptyForm())
async function fetchData() { loading.value = true; try { rows.value = (await api.get('/banks/')).data } catch(e) { $q.notify({type:'negative',message:'Failed'}) } finally { loading.value = false } }
function openCreate() { form.value = emptyForm(); editMode.value = false; dialogOpen.value = true }
function openEdit(row) { form.value = { ...row }; editId.value = row.id; editMode.value = true; dialogOpen.value = true }
async function save() { saving.value = true; try { if (editMode.value) { await api.put(`/banks/${editId.value}`, form.value); $q.notify({type:'positive',message:'Updated'}) } else { await api.post('/banks/', form.value); $q.notify({type:'positive',message:'Created'}) }; dialogOpen.value = false; await fetchData() } catch(e) { $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value = false } }
function confirmDelete(row) { $q.dialog({title:'Delete Bank',message:`Delete "${row.bank_name}"?`,cancel:true,persistent:true}).onOk(async () => { try { await api.delete(`/banks/${row.id}`); $q.notify({type:'positive',message:'Deleted'}); await fetchData() } catch(e) { $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } }) }
onMounted(fetchData)
</script>
