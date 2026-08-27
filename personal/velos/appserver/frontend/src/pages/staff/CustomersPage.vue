<template>
  <q-page padding>
    <div class="text-h5">Customers</div>
    <div class="text-subtitle2">List of customer accounts</div>

    <q-card class="q-mt-md">
      <q-card-section>
        <q-table :rows="customers" :columns="cols" row-key="id" :loading="loading" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as userService from '@/services/userService'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const customers = ref([])
const loading = ref(false)

const cols = [
  { name: 'full_name', label: 'Name', field: 'full_name' },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'created_at', label: 'Joined', field: 'created_at' }
]

async function load() {
  loading.value = true
  try {
    customers.value = await userService.listCustomers()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load customers' })
  } finally { loading.value = false }
}

onMounted(load)
</script>
