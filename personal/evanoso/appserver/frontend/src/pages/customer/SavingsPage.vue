<template>
  <q-page class="customer-flow-page">
    <div class="page-heading"><div><div class="eyebrow">A little today. More tomorrow.</div><h1 class="page-title">Savings goals</h1><p class="page-subtitle">Make room for the things that matter. Goals track your progress without moving funds.</p></div><q-btn color="primary" icon="add" label="New goal" @click="dialog = true" /></div>
    <q-banner v-if="error" class="bg-red-1 text-red-9 q-mb-md">{{ error }} <q-btn flat label="Retry" @click="load" /></q-banner>
    <q-linear-progress v-if="loading" indeterminate />
    <div class="customer-account-grid">
      <section v-for="goal in goals" :key="goal.id" class="customer-panel goal-card">
        <div class="goal-icon"><q-icon name="savings" size="28px" /></div><h2>{{ goal.name }}</h2>
        <div class="goal-amount">{{ money(goal.saved_amount) }} <small>of {{ money(goal.target_amount) }}</small></div>
        <q-linear-progress rounded size="8px" :value="Math.min(Number(goal.saved_amount) / Number(goal.target_amount), 1)" class="q-my-lg" />
        <div class="row justify-between items-center"><span class="text-grey-5">{{ Math.round(Number(goal.saved_amount) / Number(goal.target_amount) * 100) }}% complete</span><q-btn flat color="primary" label="Update progress" @click="edit(goal)" /></div>
      </section>
    </div>
    <section v-if="!loading && !goals.length" class="empty-state customer-panel"><q-icon name="savings" size="48px" /><h2>Your next chapter starts here</h2><p>Create a goal for an emergency fund, a trip, or something just for you.</p><q-btn color="primary" label="Create your first goal" @click="dialog = true" /></section>
    <q-dialog v-model="dialog"><q-card style="width:440px;max-width:95vw"><q-card-section><h2 class="section-heading">{{ selected ? 'Update your progress' : 'What are you saving for?' }}</h2></q-card-section><q-form @submit="save"><q-card-section class="q-gutter-md"><q-input v-model.trim="form.name" filled label="Goal name" maxlength="80" :rules="[v => !!v || 'Give your goal a name']" /><q-input v-model="form.target_amount" filled label="Target amount (PHP)" type="number" min="0.01" step="0.01" :rules="[v => Number(v) > 0 || 'Enter a positive target']" /><q-input v-model="form.saved_amount" filled label="Saved so far (PHP)" type="number" min="0" step="0.01" :rules="[v => Number(v) >= 0 || 'Enter zero or more']" /></q-card-section><q-card-actions align="right"><q-btn flat label="Cancel" v-close-popup /><q-btn color="primary" type="submit" label="Save goal" :loading="saving" /></q-card-actions></q-form></q-card></q-dialog>
  </q-page>
</template>
<script setup>
import { ref, watch, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
const $q = useQuasar(), goals = ref([]), loading = ref(true), saving = ref(false), error = ref(''), dialog = ref(false), selected = ref(null)
const form = ref({ name: '', target_amount: '', saved_amount: '0' })
const money = v => new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(v)
async function load () { loading.value = true; error.value = ''; try { goals.value = (await api.get('/customer/goals/')).data } catch { error.value = 'Could not load savings goals.' } finally { loading.value = false } }
function edit (goal) { selected.value = goal.id; form.value = { name: goal.name, target_amount: goal.target_amount, saved_amount: goal.saved_amount }; dialog.value = true }
watch(dialog, v => { if (!v) { selected.value = null; form.value = { name: '', target_amount: '', saved_amount: '0' } } })
async function save () { saving.value = true; try { if (selected.value) await api.put(`/customer/goals/${selected.value}`, form.value); else await api.post('/customer/goals/', form.value); dialog.value = false; await load(); $q.notify({ type: 'positive', message: 'Savings goal saved' }) } catch { $q.notify({ type: 'negative', message: 'Could not save your goal. Check the amounts and try again.' }) } finally { saving.value = false } }
onMounted(load)
</script>
