<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Accounts</div>
      <q-space />
      <q-btn color="teal" icon="add" label="Open Account" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-available_balance="props">
        <q-td :props="props" class="text-right">₱{{ Number(props.row.available_balance).toLocaleString('en-PH', {minimumFractionDigits:2}) }}</q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section><div class="text-h6">Open New Account</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model="form.account_number" label="Account Number" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model.number="form.customer_id" label="Customer ID" outlined dense type="number" :rules="[v=>!!v||'Required']" />
            <q-input v-model.number="form.account_type_id" label="Account Type ID" outlined dense type="number" :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.branch_code" label="Branch Code" outlined dense />
            <div class="row justify-end q-gutter-sm q-mt-md"><q-btn flat label="Cancel" @click="dialogOpen=false" /><q-btn type="submit" color="teal" label="Create" :loading="saving" /></div>
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
const rows = ref([]), loading = ref(false), saving = ref(false), dialogOpen = ref(false)
const columns = [
  { name:'id',label:'ID',field:'id',sortable:true,align:'left' },
  { name:'account_number',label:'Account #',field:'account_number',align:'left' },
  { name:'customer_id',label:'Customer',field:'customer_id',align:'left' },
  { name:'available_balance',label:'Balance',field:'available_balance',align:'right' },
  { name:'status',label:'Status',field:'status',align:'left' },
]
const form = ref({ account_number:'',customer_id:null,account_type_id:null,currency_code:'PHP',branch_code:'' })
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/accounts/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
function openCreate() { form.value={ account_number:'',customer_id:null,account_type_id:null,currency_code:'PHP',branch_code:'' }; dialogOpen.value=true }
async function save() { saving.value=true; try { await api.post('/accounts/',form.value); $q.notify({type:'positive',message:'Account created'}); dialogOpen.value=false; await fetchData() } catch(e){ $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value=false } }
onMounted(fetchData)
</script>
