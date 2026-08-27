<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Fee Types</div>
      <q-space />
      <q-btn color="primary" icon="add" label="Add Fee Type" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props"><q-btn flat dense icon="edit" color="primary" @click="openEdit(props.row)" size="sm" /><q-btn flat dense icon="delete" color="negative" @click="confirmDelete(props.row)" size="sm" /></q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 450px; max-width: 95vw">
        <q-card-section><div class="text-h6">{{ editMode ? 'Edit' : 'Create' }} Fee Type</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.fee_code" label="Fee Code" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.fee_name" label="Fee Name" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.fee_description" label="Description" outlined dense type="textarea" autogrow />
            <q-input v-model="form.fixed_amount" label="Fixed Amount" outlined dense type="number" />
            <q-input v-model="form.percentage_rate" label="Percentage Rate" outlined dense type="number" />
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
  { name:'fee_code',label:'Code',field:'fee_code',align:'left' },
  { name:'fee_name',label:'Name',field:'fee_name',align:'left' },
  { name:'fixed_amount',label:'Fixed Amt',field:'fixed_amount',align:'right' },
  { name:'percentage_rate',label:'Rate %',field:'percentage_rate',align:'right' },
  { name:'actions',label:'Actions',field:'actions',align:'center' },
]
const emptyForm = () => ({ fee_code:'',fee_name:'',fee_description:'',fixed_amount:0,percentage_rate:0 })
const form = ref(emptyForm())
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/fee-types/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
function openCreate() { form.value=emptyForm(); editMode.value=false; dialogOpen.value=true }
function openEdit(row) { form.value={...row}; editId.value=row.id; editMode.value=true; dialogOpen.value=true }
async function save() { saving.value=true; try { if(editMode.value){await api.put(`/fee-types/${editId.value}`,form.value);$q.notify({type:'positive',message:'Updated'})}else{await api.post('/fee-types/',form.value);$q.notify({type:'positive',message:'Created'})}; dialogOpen.value=false; await fetchData() } catch(e){ $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value=false } }
function confirmDelete(row){ $q.dialog({title:'Delete',message:`Delete "${row.fee_name}"?`,cancel:true,persistent:true}).onOk(async()=>{ try{await api.delete(`/fee-types/${row.id}`);$q.notify({type:'positive',message:'Deleted'});await fetchData()}catch(e){$q.notify({type:'negative',message:e.response?.data?.detail||'Failed'})} }) }
onMounted(fetchData)
</script>
