<template>
  <section class="mobile-transfer-flow">
    <template v-if="step === 'recipient'">
      <q-input v-model="search" filled dense placeholder="Search name or account number" aria-label="Search recipients"><template #prepend><q-icon name="search" /></template></q-input>
      <div class="transfer-tabs">
        <q-btn v-for="tab in tabs" :key="tab.label" flat stack :icon="tab.icon" :label="tab.label" :class="{ selected: mode === tab.label }" @click="tab.label === 'Code' ? $emit('scan') : mode = tab.label" />
      </div>
      <q-form v-if="mode === 'Transfer'" class="customer-form" @submit="selectRecipient({ account_number: destination, name: 'Bembank recipient' })">
        <q-input v-model.trim="destination" filled label="To account number" :rules="[v => !!v || 'Enter an account number']" />
        <q-btn color="primary" label="Continue" type="submit" unelevated />
      </q-form>
      <q-list v-else class="recipient-list">
        <q-item v-for="person in people" :key="person.account_number" clickable @click="selectRecipient(person)">
          <q-item-section avatar><q-avatar class="recipient-avatar">{{ initials(person.name) }}</q-avatar></q-item-section>
          <q-item-section><q-item-label>{{ person.name }}</q-item-label><q-item-label caption>Bembank · {{ person.account_number }}</q-item-label></q-item-section>
          <q-item-section side><q-icon name="chevron_right" /></q-item-section>
        </q-item>
        <p v-if="!people.length" class="page-subtitle q-pa-md">{{ loading ? 'Loading recipients…' : 'No recipients found. Use Transfer to enter an account number.' }}</p>
      </q-list>
    </template>
    <q-form v-else class="mobile-amount-form" @submit="$emit('review')">
      <q-btn flat dense icon="chevron_left" label="Change recipient" @click="step = 'recipient'" />
      <div class="recipient-summary"><q-avatar class="recipient-avatar">{{ initials(selectedName) }}</q-avatar><div><strong>{{ selectedName }}</strong><small>Bembank · {{ modelValue.destination_account_number }}</small></div></div>
      <q-select :model-value="modelValue.source_account_id" @update:model-value="update('source_account_id', $event)" :options="accounts" emit-value map-options filled dense label="From account" :rules="[v => !!v || 'Choose a source account']" />
      <q-input :model-value="modelValue.amount" @update:model-value="update('amount', $event)" class="transfer-amount" prefix="₱" inputmode="decimal" aria-label="Amount (PHP)" placeholder="0.00" :rules="[v => Number(v) > 0 || 'Enter an amount greater than zero']" />
      <q-input :model-value="modelValue.remarks" @update:model-value="update('remarks', $event)" filled dense placeholder="Add a note (optional)" aria-label="Note (optional)" maxlength="50" counter />
      <div class="amount-keypad"><q-btn v-for="key in ['1','2','3','4','5','6','7','8','9','.','0','⌫']" :key="key" flat :label="key" :aria-label="key === '⌫' ? 'Delete digit' : key" @click="digit(key)" /></div>
      <q-btn type="submit" label="Next" color="primary" unelevated :loading="busy" :disable="loading || !accounts.length" />
    </q-form>
  </section>
</template>
<script setup>
import { computed, ref, watch } from 'vue'
const props = defineProps({ modelValue: Object, accounts: Array, recipients: Array, recent: Array, loading: Boolean, busy: Boolean })
const emit = defineEmits(['update:modelValue', 'review', 'scan'])
const step = ref('recipient'), mode = ref('Contacts'), search = ref(''), destination = ref(''), selectedName = ref('Bembank recipient')
const tabs = [{ label: 'Contacts', icon: 'person_outline' }, { label: 'Transfer', icon: 'account_balance_wallet' }, { label: 'Code', icon: 'qr_code' }, { label: 'Recent', icon: 'history' }]
const people = computed(() => (mode.value === 'Recent' ? props.recent : props.recipients).filter(p => `${p.name} ${p.account_number}`.toLowerCase().includes(search.value.toLowerCase())))
const initials = name => (name || 'B').split(/\s+/).slice(0, 2).map(s => s[0]).join('').toUpperCase()
function update (key, value) { emit('update:modelValue', { ...props.modelValue, [key]: value }) }
function selectRecipient (person) { selectedName.value = person.name; update('destination_account_number', person.account_number); step.value = 'amount' }
function digit (key) { const value = String(props.modelValue.amount || ''); if (key === '⌫') update('amount', value.slice(0, -1)); else if (/^\d{0,12}(\.\d{0,2})?$/.test(value + key)) update('amount', value + key) }
watch(() => props.modelValue.destination_account_number, value => { if (value) step.value = 'amount'; else step.value = 'recipient' })
watch(() => props.accounts, accounts => { if (!props.modelValue.source_account_id && accounts.length === 1) update('source_account_id', accounts[0].value) })
</script>
