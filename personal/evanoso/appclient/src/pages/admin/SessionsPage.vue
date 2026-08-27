<template>
  <div>
    <div class="text-h5 q-mb-md text-weight-bold">Sessions</div>
    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered dense>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="!props.row.revoked_at" flat dense icon="block" color="warning" label="Revoke" @click="revokeSession(props.row)" size="sm" />
          <q-chip v-else dense color="red" text-color="white" size="sm">Revoked</q-chip>
        </q-td>
      </template>
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
  { name:'ip_address',label:'IP',field:'ip_address',align:'left' },
  { name:'login_at',label:'Login At',field:'login_at',align:'left',format:v=>v?new Date(v).toLocaleString():'' },
  { name:'expires_at',label:'Expires',field:'expires_at',align:'left',format:v=>v?new Date(v).toLocaleString():'' },
  { name:'actions',label:'Status',field:'actions',align:'center' },
]
async function fetchData() { loading.value=true; try { rows.value=(await api.get('/sessions/')).data } catch(e){ $q.notify({type:'negative',message:'Failed'}) } finally { loading.value=false } }
async function revokeSession(row) { try { await api.put(`/sessions/${row.id}/revoke`); $q.notify({type:'positive',message:'Session revoked'}); await fetchData() } catch(e){ $q.notify({type:'negative',message:'Failed'}) } }
onMounted(fetchData)
</script>
