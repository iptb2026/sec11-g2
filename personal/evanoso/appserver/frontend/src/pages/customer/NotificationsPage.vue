<template>
  <q-page class="customer-flow-page">
    <div class="page-heading"><div><div class="eyebrow">STAY IN THE KNOW</div><h1 class="page-title">Activity alerts</h1><p class="page-subtitle">Transactions, requests, and account updates. {{ unread.length }} unread.</p></div><div class="row q-gutter-sm"><q-btn outline color="primary" icon="refresh" label="Refresh" @click="load" :loading="loading" /><q-btn flat color="primary" label="Mark all as read" :disable="!unread.length || busy" @click="markRead(unread.map(row => row.id))" /></div></div>
    <q-banner v-if="error" class="bank-feedback q-mb-md">{{ error }}</q-banner><q-toggle v-model="onlyUnread" label="Unread only" class="q-mb-md" /><q-linear-progress v-if="loading" indeterminate />
    <section class="customer-panel"><div v-for="row in visible" :key="row.id" class="activity-row"><div class="activity-icon"><q-icon :name="row.read ? 'notifications_none' : 'notifications_active'" /></div><div class="activity-detail"><strong>{{ row.title }}<template v-if="row.amount !== null"> · {{ money(row.amount) }}</template> <q-badge v-if="!row.read" color="primary" label="New" /></strong><small>{{ row.status }} · {{ new Date(row.date).toLocaleString('en-PH') }}</small><small>{{ row.reference }}</small></div><q-btn v-if="!row.read" flat round icon="done" aria-label="Mark as read" :disable="busy" @click="markRead([row.id])" /><q-btn flat round icon="chevron_right" :to="row.to" aria-label="View activity details" /></div><div v-if="!loading && !visible.length" class="empty-state"><q-icon name="notifications_none" size="40px" /><h2>You're all caught up</h2><p>New account activity will appear here.</p></div></section>
  </q-page>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
const rows = ref([]), error = ref(''), loading = ref(false), busy = ref(false), onlyUnread = ref(false)
const unread = computed(() => rows.value.filter(row => !row.read))
const visible = computed(() => onlyUnread.value ? unread.value : rows.value)
const money = value => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(value)
async function load () { loading.value = true; error.value = ''; try { rows.value = (await api.get('/customer/alerts/')).data } catch { error.value = 'Could not load account activity. Please retry.' } finally { loading.value = false } }
async function markRead (ids) { busy.value = true; error.value = ''; try { await api.post('/customer/alerts/read', { ids }); rows.value = rows.value.map(row => ids.includes(row.id) ? { ...row, read: true } : row) } catch { error.value = 'Could not update alerts. Please try again.' } finally { busy.value = false } }
onMounted(load)
</script>
