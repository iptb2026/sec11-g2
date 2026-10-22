<template><section class="customer-panel q-mt-lg"><h2 class="section-heading">Active sessions</h2><p class="page-subtitle q-mb-md">Sign out a device you no longer use. Sessions expire after 30 minutes.</p><q-banner v-if="error" class="bg-red-1 text-red-9">{{ error }}<q-btn flat label="Retry" @click="load" /></q-banner><q-linear-progress v-if="loading" indeterminate /><div v-for="session in sessions" :key="session.id" class="activity-row"><div class="activity-icon"><q-icon name="devices" /></div><div class="activity-detail"><strong>{{ session.current ? 'This device' : 'Other session' }}</strong><small>{{ session.user_agent || 'Unknown device' }}</small><small>{{ new Date(session.login_at).toLocaleString('en-PH') }}</small></div><q-btn flat color="negative" label="Sign out" :loading="busy === session.id" @click="revoke(session)" /></div></section></template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'
const sessions = ref([]), error = ref(''), busy = ref(null), loading = ref(false), auth = useAuthStore(), router = useRouter()
async function load () { loading.value = true; error.value = ''; try { sessions.value = (await api.get('/auth/sessions')).data } catch { error.value = 'Could not load sessions.' } finally { loading.value = false } }
async function revoke (session) { busy.value = session.id; try { await api.delete(`/auth/sessions/${session.id}`); if (session.current) { await auth.logout(false); router.replace('/login') } else await load() } catch { error.value = 'Could not sign out this session.' } finally { busy.value = null } }
onMounted(load)
</script>
