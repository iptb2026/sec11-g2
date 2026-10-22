<template>
  <q-page padding>
    <div class="row items-center justify-between">
      <div>
        <div class="text-h5">Welcome back, Alex</div>
        <div class="text-subtitle2">System Monitoring — Admin</div>
      </div>
      <role-badge role="admin" />
    </div>

    <div class="q-mt-lg row q-gutter-md">
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-subtitle2">Total Users</div>
          <div class="text-h6">{{ stats.totalUsers }}</div>
        </q-card-section>
      </q-card>
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-subtitle2">Active Users</div>
          <div class="text-h6">{{ stats.activeUsers }}</div>
        </q-card-section>
      </q-card>
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-subtitle2">Staff</div>
          <div class="text-h6">{{ stats.staff }}</div>
        </q-card-section>
      </q-card>
      <q-card class="col-12 col-md-3">
        <q-card-section>
          <div class="text-subtitle2">Customers</div>
          <div class="text-h6">{{ stats.customers }}</div>
        </q-card-section>
      </q-card>
    </div>

    <div class="q-mt-lg row">
      <q-card class="col-12">
        <q-card-section>
          <div class="text-h6">Recent Activity</div>
          <q-table :rows="activities" :columns="activityCols" row-key="id" dense flat />
        </q-card-section>
      </q-card>
    </div>

    <div class="q-mt-lg">
      <q-card>
        <q-card-section>
          <div class="text-h6">Recently Registered Users</div>
          <q-table :rows="recentUsers" :columns="userCols" row-key="id" dense flat />
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import RoleBadge from '@/components/RoleBadge.vue'
import { listUsers } from '@/services/userService'

const stats = ref({ totalUsers: 0, activeUsers: 0, staff: 0, customers: 0 })
const activities = ref([])
const recentUsers = ref([])

const activityCols = [
  { name: 'user', label: 'User', field: 'user' },
  { name: 'action', label: 'Action', field: 'action' },
  { name: 'role', label: 'Role', field: 'role' },
  { name: 'created_at', label: 'Date', field: 'created_at' }
]

const userCols = [
  { name: 'full_name', label: 'Name', field: 'full_name' },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'role_code', label: 'Role', field: 'role_code' },
  { name: 'created_at', label: 'Registered', field: 'created_at' },
  { name: 'is_active', label: 'Status', field: 'is_active' }
]

onMounted(async () => {
  try {
    const users = await listUsers()
    stats.value.totalUsers = users.length
    stats.value.activeUsers = users.filter(u => u.is_active).length
    stats.value.staff = users.filter(u => u.role_code === 'staff').length
    stats.value.customers = users.filter(u => u.role_code === 'customer').length
    recentUsers.value = users.slice().sort((a,b)=> new Date(b.created_at)-new Date(a.created_at)).slice(0,6)

    activities.value = users.slice(0,10).map(u => ({ id: u.id, user: u.full_name, action: 'Registered', role: u.role_code, created_at: u.created_at }))
  } catch (err) {
    // if unauthorized, user will be redirected elsewhere by api handling
  }
})
</script>
