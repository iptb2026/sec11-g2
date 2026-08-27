<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Accounts</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Create Account" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props"><q-btn flat dense icon="edit" color="primary" @click="openEdit(props.row)" size="sm" /><q-btn flat dense icon="delete" color="negative" @click="confirmDelete(props.row)" size="sm" /></q-td>
      </template>
      <template v-slot:body-cell-available_balance="props">
        <q-td :props="props" class="text-right">₱{{ Number(props.row.available_balance).toLocaleString('en-PH', {minimumFractionDigits:2}) }}</q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section><div class="text-h6">{{ editMode ? 'Edit' : 'Create' }} Account</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.account_number" label="Account Number" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model.number="form.customer_id" label="Customer ID" outlined dense type="number" :rules="[v=>!!v||'Required']" />
            <q-input v-model.number="form.account_type_id" label="Account Type ID" outlined dense type="number" :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.currency_code" label="Currency" outlined dense />
            <q-input v-model="form.branch_code" label="Branch Code" outlined dense />
            <q-select v-if="editMode" v-model="form.status" :options="['ACTIVE','FROZEN','CLOSED']" label="Status" outlined dense />
            <div class="row justify-end q-gutter-sm q-mt-md"><q-btn flat label="Cancel" @click="dialogOpen=false" /><q-btn type="submit" color="primary" :label="editMode?'Update':'Create'" :loading="saving" /></div>
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
  { name:'id',label:'ID',field:'id',sortable:true,align:'left' },
  { name:'account_number',label:'Account #',field:'account_number',align:'left' },
  { name:'customer_id',label:'Customer',field:'customer_id',align:'left' },
  { name:'account_type_id',label:'Type',field:'account_type_id',align:'left' },
  { name:'available_balance',label:'Balance',field:'available_balance',align:'right' },
  { name:'status',label:'Status',field:'status',align:'left' },
  { name:'actions',label:'Actions',field:'actions',align:'center' },
]
const emptyForm = () => ({ account_number:'',customer_id:null,account_type_id:null,currency_code:'PHP',branch_code:'' })
const form = ref(emptyForm())
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/accounts/')).data } catch(e){ $q.notify({type:'negative',message:'Failed to load accounts'}) } finally { loading.value=false } }
function openCreate() { form.value=emptyForm(); editMode.value=false; dialogOpen.value=true }
function openEdit(row) { form.value={...row}; editId.value=row.id; editMode.value=true; dialogOpen.value=true }
async function save() { saving.value=true; try { if(editMode.value){await api.put(`/accounts/${editId.value}`,form.value);$q.notify({type:'positive',message:'Updated'})}else{await api.post('/accounts/',form.value);$q.notify({type:'positive',message:'Created'})}; dialogOpen.value=false; await fetchData() } catch(e){ $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value=false } }
function confirmDelete(row){ $q.dialog({title:'Delete Account',message:`Delete account "${row.account_number}"?`,cancel:true,persistent:true}).onOk(async()=>{ try{await api.delete(`/accounts/${row.id}`);$q.notify({type:'positive',message:'Deleted'});await fetchData()}catch(e){$q.notify({type:'negative',message:e.response?.data?.detail||'Failed'})} }) }
onMounted(fetchData)
</script>
