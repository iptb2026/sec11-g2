<template><section class="customer-panel q-mt-lg"><h2 class="section-heading">App settings</h2><p class="page-subtitle">These preferences are saved for your account on this browser.</p><q-toggle v-model="settings.hideBalance" label="Hide dashboard balance when opening the app" @update:model-value="save" /><q-toggle v-model="settings.reduceMotion" label="Reduce animations" @update:model-value="save" /><q-banner v-if="error" class="bank-feedback">{{ error }}</q-banner><div class="q-mt-md"><q-btn outline icon="help_outline" label="Help & support" to="/help" /></div></section></template>
<script setup>
import {ref} from 'vue'
import {useAuthStore} from '@/stores/auth-store'
import {preferences,savePreferences} from '@/utils/preferences'
const auth=useAuthStore(),settings=ref(preferences(auth.userId)),error=ref('')
function save(){error.value=savePreferences(auth.userId,settings.value)?'':'Your browser could not save these preferences.'}
</script>
