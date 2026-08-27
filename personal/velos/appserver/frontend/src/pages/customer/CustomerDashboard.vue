<template>
  <q-page padding>
    <div class="text-h5">Welcome, {{ user?.full_name }}</div>
    <div class="text-subtitle2">Customer Dashboard</div>

    <div class="q-mt-md row">
      <q-card class="col-12 col-md-6">
        <q-card-section>
          <div class="text-subtitle2">Account Status</div>
          <div>{{ user?.is_active ? 'Active' : 'Inactive' }}</div>
        </q-card-section>
      </q-card>

      <q-card class="col-12 col-md-6">
        <q-card-section>
          <q-btn label="My Profile" to="/customer/profile" color="primary" />
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { currentUser, loadMe } = useAuth()
const user = currentUser

onMounted(async () => {
  if (!user.value) await loadMe()
})
</script>
