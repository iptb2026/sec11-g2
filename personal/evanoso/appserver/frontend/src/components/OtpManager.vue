<template>
  <section class="customer-panel q-mt-lg">
    <div class="row items-center justify-between q-gutter-sm"><div><h2 class="section-heading">Authenticator verification</h2><p class="page-subtitle">Add a one-time code to your password when you sign in.</p></div><q-badge :color="enabled ? 'positive' : 'grey-7'">{{ enabled ? 'Enabled' : 'Not enabled' }}</q-badge></div>
    <q-linear-progress v-if="loading" indeterminate class="q-mt-md" />
    <q-banner v-if="loadError" class="bank-feedback q-mt-md">{{ loadError }}<q-btn flat label="Retry" @click="load" /></q-banner>
    <div v-else-if="!loading" class="q-mt-lg">
      <template v-if="enabled"><p class="page-subtitle">{{ remaining }} recovery codes remaining. Keep them somewhere private in case you lose access to your authenticator.</p><q-btn outline color="negative" label="Turn off authenticator" class="q-mt-md" @click="begin('disable')" /></template>
      <template v-else><p class="page-subtitle q-mb-md">Use Google Authenticator, Microsoft Authenticator, or another compatible app. You'll scan a QR code and confirm your first code.</p><q-btn color="primary" icon="security" label="Set up authenticator" @click="begin('setup')" /></template>
    </div>
    <q-dialog v-model="open" persistent @hide="clearSecrets">
      <q-card class="otp-dialog">
        <q-card-section><h2 class="section-heading">{{ stage === 'recovery' ? 'Save your recovery codes' : mode === 'disable' ? 'Turn off authenticator' : stage === 'scan' ? 'Connect your authenticator' : 'Set up authenticator' }}</h2><q-banner v-if="error" class="bank-feedback" role="alert">{{ error }}</q-banner></q-card-section>
        <q-form v-if="stage === 'password'" @submit="mode === 'disable' ? disable() : setup()">
          <q-card-section class="q-gutter-md"><p class="page-subtitle">Confirm your current password to continue.</p><q-input v-model="password" filled type="password" autocomplete="current-password" label="Current password" :rules="[v => !!v || 'Enter your password']" /><q-input v-if="mode === 'disable'" v-model.trim="code" filled autocomplete="one-time-code" label="Authenticator or recovery code" maxlength="32" :rules="[v => v.length >= 6 || 'Enter a valid code']" /><p v-if="mode === 'disable'" class="page-subtitle">Future sign-ins will use only your password. Other devices will be signed out.</p></q-card-section>
          <q-card-actions align="right"><q-btn flat label="Cancel" :disable="busy" v-close-popup /><q-btn color="primary" :label="mode === 'disable' ? 'Turn off' : 'Continue'" type="submit" :loading="busy" /></q-card-actions>
        </q-form>
        <q-form v-else-if="stage === 'scan'" @submit="confirm">
          <q-card-section class="q-gutter-md"><p class="page-subtitle">Scan this QR code in your authenticator app, then enter its current six-digit code. Setup expires in 10 minutes.</p><div class="text-center"><img :src="qrImage" alt="Scan to set up Bembank in your authenticator" width="240" height="240" /></div><q-expansion-item label="Can't scan? Enter the setup key manually"><p class="otp-secret q-pa-md">{{ secret }}</p></q-expansion-item><q-input v-model="code" filled label="Six-digit code" inputmode="numeric" autocomplete="one-time-code" maxlength="6" :rules="[v => /^[0-9]{6}$/.test(v) || 'Enter all six digits']" /></q-card-section>
          <q-card-actions align="right"><q-btn flat label="Cancel setup" :disable="busy" v-close-popup /><q-btn color="primary" label="Enable verification" type="submit" :loading="busy" /></q-card-actions>
        </q-form>
        <template v-else><q-card-section><p class="page-subtitle q-mb-md">Authenticator verification is on. Each recovery code works once. These codes are only shown now.</p><div class="recovery-grid"><code v-for="item in recoveryCodes" :key="item">{{ item }}</code></div><q-btn outline icon="download" label="Download recovery codes" class="q-my-md" @click="downloadCodes" /><q-checkbox v-model="saved" label="I saved my recovery codes somewhere safe" /></q-card-section><q-card-actions align="right"><q-btn color="primary" label="Done" :disable="!saved" v-close-popup /></q-card-actions></template>
      </q-card>
    </q-dialog>
  </section>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import QRCode from 'qrcode'
import api from '@/services/api'
const emit = defineEmits(['changed'])
const enabled = ref(false), remaining = ref(0), loading = ref(true), loadError = ref(''), open = ref(false), mode = ref('setup'), stage = ref('password'), busy = ref(false), error = ref(''), password = ref(''), code = ref(''), secret = ref(''), qrImage = ref(''), recoveryCodes = ref([]), saved = ref(false)
async function load () { loading.value = true; loadError.value = ''; try { const { data } = await api.get('/auth/otp/status'); enabled.value = data.enabled; remaining.value = data.recovery_codes_remaining } catch { loadError.value = 'Verification settings could not be loaded.' } finally { loading.value = false } }
function clearSecrets () { password.value = ''; code.value = ''; secret.value = ''; qrImage.value = ''; recoveryCodes.value = []; saved.value = false }
function begin (action) { clearSecrets(); mode.value = action; stage.value = 'password'; error.value = ''; open.value = true }
function fail (e) { error.value = typeof e.response?.data?.detail === 'string' && e.response.status < 500 ? e.response.data.detail : 'Could not update verification. Please try again.' }
async function setup () { busy.value = true; error.value = ''; try { const { data } = await api.post('/auth/otp/setup', { password: password.value }); secret.value = data.secret; qrImage.value = await QRCode.toDataURL(data.provisioning_uri, { width: 240, margin: 2 }); password.value = ''; stage.value = 'scan' } catch (e) { fail(e) } finally { busy.value = false } }
async function confirm () { busy.value = true; error.value = ''; try { const { data } = await api.post('/auth/otp/confirm', { code: code.value }); recoveryCodes.value = data.recovery_codes; secret.value = ''; qrImage.value = ''; code.value = ''; stage.value = 'recovery'; enabled.value = true; remaining.value = data.recovery_codes.length; emit('changed') } catch (e) { fail(e) } finally { busy.value = false } }
async function disable () { busy.value = true; error.value = ''; try { await api.post('/auth/otp/disable', { password: password.value, code: code.value }); enabled.value = false; remaining.value = 0; open.value = false; emit('changed') } catch (e) { fail(e) } finally { busy.value = false } }
function downloadCodes () { const url = URL.createObjectURL(new Blob(['Bembank recovery codes\nKeep private. Each code can be used once.\n\n' + recoveryCodes.value.join('\n')], { type: 'text/plain' })); const link = document.createElement('a'); link.href = url; link.download = 'bembank-recovery-codes.txt'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000) }
onMounted(load)
</script>
<style scoped>
.otp-dialog { width: 520px; max-width: 95vw; }
.otp-secret { overflow-wrap: anywhere; font-family: monospace; letter-spacing: 2px; }
.recovery-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.recovery-grid code { border: 1px solid #304766; padding: 10px; border-radius: 7px; font-size: 12px; text-align: center; }
@media (max-width: 480px) { .recovery-grid { grid-template-columns: 1fr; } }
</style>
