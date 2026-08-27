<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Account Types</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add Type" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props"><q-btn flat dense icon="edit" color="primary" @click="openEdit(props.row)" size="sm" /><q-btn flat dense icon="delete" color="negative" @click="confirmDelete(props.row)" size="sm" /></q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section><div class="text-h6">{{ editMode ? 'Edit' : 'Create' }} Account Type</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.type_code" label="Type Code" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.type_name" label="Type Name" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.minimum_balance" label="Minimum Balance" outlined dense type="number" />
            <q-input v-model="form.opening_deposit" label="Opening Deposit" outlined dense type="number" />
            <q-input v-model="form.annual_interest_rate" label="Annual Interest Rate" outlined dense type="number" />
            <q-input v-model="form.daily_withdrawal_limit" label="Daily Withdrawal Limit" outlined dense type="number" />
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
  { name:'type_code',label:'Code',field:'type_code',align:'left' },
  { name:'type_name',label:'Name',field:'type_name',align:'left' },
  { name:'minimum_balance',label:'Min Balance',field:'minimum_balance',align:'right' },
  { name:'opening_deposit',label:'Opening Deposit',field:'opening_deposit',align:'right' },
  { name:'actions',label:'Actions',field:'actions',align:'center' },
]
const emptyForm = () => ({ type_code:'',type_name:'',minimum_balance:0,opening_deposit:0,annual_interest_rate:0,daily_withdrawal_limit:0 })
const form = ref(emptyForm())
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/account-types/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
function openCreate() { form.value=emptyForm(); editMode.value=false; dialogOpen.value=true }
function openEdit(row) { form.value={...row}; editId.value=row.id; editMode.value=true; dialogOpen.value=true }
async function save() { saving.value=true; try { if(editMode.value){await api.put(`/account-types/${editId.value}`,form.value);$q.notify({type:'positive',message:'Updated'})}else{await api.post('/account-types/',form.value);$q.notify({type:'positive',message:'Created'})}; dialogOpen.value=false; await fetchData() } catch(e){ $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value=false } }
function confirmDelete(row){ $q.dialog({title:'Delete',message:`Delete "${row.type_name}"?`,cancel:true,persistent:true}).onOk(async()=>{ try{await api.delete(`/account-types/${row.id}`);$q.notify({type:'positive',message:'Deleted'});await fetchData()}catch(e){$q.notify({type:'negative',message:e.response?.data?.detail||'Failed'})} }) }
onMounted(fetchData)
</script>
