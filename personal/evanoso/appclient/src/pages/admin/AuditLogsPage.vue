<template>
  <div>
    <div class="text-h5 q-mb-md text-weight-bold">Audit Logs</div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
    </q-table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '../../api'
const $q = useQuasar()
const rows = ref([]), loading = ref(false)
const columns = [
  { name:'id',label:'ID',field:'id',sortable:true,align:'left' },
  { name:'user_id',label:'User ID',field:'user_id',align:'left' },
  { name:'action_type',label:'Action',field:'action_type',align:'left' },
  { name:'entity_name',label:'Entity',field:'entity_name',align:'left' },
  { name:'entity_id',label:'Entity ID',field:'entity_id',align:'left' },
  { name:'action_timestamp',label:'Timestamp',field:'action_timestamp',align:'left',format:v=>v?new Date(v).toLocaleString():'' },
]
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/audit-logs/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
onMounted(fetchData)
</script>
