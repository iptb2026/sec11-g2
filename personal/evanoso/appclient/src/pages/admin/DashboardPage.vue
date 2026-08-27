<template>
  <div>
    <div class="text-h5 q-mb-md text-weight-bold">Admin Dashboard</div>
    <div class="row q-gutter-md">
      <q-card v-for="card in cards" :key="card.label" class="col-12 col-sm-5 col-md-3" flat bordered>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon :name="card.icon" size="40px" :color="card.color" />
          <div>
            <div class="text-h6">{{ card.count }}</div>
            <div class="text-caption text-grey">{{ card.label }}</div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const cards = ref([
  { label: 'Users', icon: 'people', color: 'primary', count: '...' },
  { label: 'Roles', icon: 'security', color: 'orange', count: '...' },
  { label: 'Accounts', icon: 'account_box', color: 'teal', count: '...' },
  { label: 'Banks', icon: 'account_balance', color: 'deep-purple', count: '...' },
])

onMounted(async () => {
  try {
    const [users, roles, accounts, banks] = await Promise.all([
      api.get('/users/'),
      api.get('/roles/'),
      api.get('/accounts/'),
      api.get('/banks/'),
    ])
    cards.value[0].count = users.data.length
    cards.value[1].count = roles.data.length
    cards.value[2].count = accounts.data.length
    cards.value[3].count = banks.data.length
  } catch (e) {
    // Non-critical — dashboard still renders
  }
})
</script>
