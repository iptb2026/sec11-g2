<template>
  <q-page padding>
    <div class="text-h5">My Profile</div>
    <div class="q-mt-md">
      <q-card>
        <q-card-section>
          <q-form @submit.prevent="save">
            <q-input v-model="form.full_name" label="Full name" />
            <q-input v-model="form.email" label="Email" />
            <q-input v-model="form.password" label="New password" type="password" />
            <div class="q-mt-md">
              <q-btn label="Save" color="primary" type="submit" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()
const { currentUser, loadMe } = useAuth()

const form = ref({ full_name: '', email: '', password: '' })

onMounted(async () => {
  if (!currentUser.value) await loadMe()
  form.value.full_name = currentUser.value.full_name
  form.value.email = currentUser.value.email
})

async function save() {
  try {
    await api.put('/users/me', { full_name: form.value.full_name, email: form.value.email, password: form.value.password })
    $q.notify({ type: 'positive', message: 'Profile updated' })
    await loadMe()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Update failed' })
  }
}
</script>
