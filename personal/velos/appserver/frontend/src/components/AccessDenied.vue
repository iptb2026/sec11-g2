<template>
  <q-page class="flex flex-center q-pa-xl">
    <q-card class="q-pa-lg" style="max-width:520px; width:100%">
      <div class="text-center">
        <div class="text-h2">🔒</div>
        <div class="text-h4 q-mt-md">Access Denied</div>
        <p class="q-mt-md">You don't have permission to access this resource.</p>
        <div class="q-mt-md">
          <div><strong>Current role:</strong> {{ currentRole || 'Unknown' }}</div>
          <div v-if="requiredRole"><strong>Required role:</strong> {{ requiredRole }}</div>
        </div>
        <q-btn class="q-mt-lg" label="Return to Dashboard" color="primary" @click="goHome" />
      </div>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter, useRoute } from 'vue-router'

const { currentUser } = useAuth()
const router = useRouter()
const route = useRoute()

const currentRole = computed(() => currentUser.value?.role_code)
const requiredRole = route.meta?.roles ? route.meta.roles.join(', ') : null

function goHome() {
  if (currentRole.value === 'admin') router.push('/admin/dashboard')
  else if (currentRole.value === 'staff') router.push('/staff/dashboard')
  else router.push('/customer/dashboard')
}
</script>
