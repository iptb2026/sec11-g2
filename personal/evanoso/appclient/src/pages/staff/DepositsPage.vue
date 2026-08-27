<template>
  <div>
    <div class="row items-center q-mb-md">
      <div class="text-h5 text-weight-bold">Process Deposit</div>
      <q-space />
      <q-btn color="green" icon="savings" label="New Deposit" @click="openCreate" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-amount="props">
        <q-td :props="props" class="text-right text-positive text-weight-bold">+₱{{ Number(props.row.amount).toLocaleString('en-PH',{minimumFractionDigits:2}) }}</q-td>
      </template>
    </q-table>
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="width: 500px; max-width: 95vw">
        <q-card-section><div class="text-h6">Process Deposit</div></q-card-section>
        <q-card-section>
          <q-form @submit.prevent="save" class="q-gutter-sm">
            <q-input v-model.number="form.account_id" label="Account ID" outlined dense type="number" :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.reference_number" label="Reference Number" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model.number="form.amount" label="Amount" outlined dense type="number" prefix="₱" :rules="[v=>v>0||'Must be > 0']" />
            <q-select v-model="form.deposit_channel" :options="['CASH','ATM','ONLINE','INTERBANK']" label="Channel" outlined dense :rules="[v=>!!v||'Required']" />
            <q-input v-model="form.remarks" label="Remarks" outlined dense type="textarea" autogrow />
            <div class="row justify-end q-gutter-sm q-mt-md"><q-btn flat label="Cancel" @click="dialogOpen=false" /><q-btn type="submit" color="green" label="Process" :loading="saving" /></div>
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
  { name:'account_id',label:'Account',field:'account_id',align:'left' },
  { name:'reference_number',label:'Reference',field:'reference_number',align:'left' },
  { name:'amount',label:'Amount',field:'amount',align:'right' },
  { name:'deposit_channel',label:'Channel',field:'deposit_channel',align:'left' },
  { name:'transaction_date',label:'Date',field:'transaction_date',align:'left',format:v=>v?new Date(v).toLocaleString():'' },
]
const emptyForm = () => ({ account_id:null,reference_number:'',amount:0,deposit_channel:'CASH',deposited_by_user_id:null,remarks:'',transaction_date:new Date().toISOString() })
const form = ref(emptyForm())
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/deposits/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
function openCreate() { form.value=emptyForm(); dialogOpen.value=true }
async function save() { saving.value=true; try { await api.post('/deposits/',form.value); $q.notify({type:'positive',message:'Deposit processed'}); dialogOpen.value=false; await fetchData() } catch(e){ $q.notify({type:'negative',message:e.response?.data?.detail||'Failed'}) } finally { saving.value=false } }
onMounted(fetchData)
</script>
