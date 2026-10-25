<template>
  <q-layout view="lHh Lpr lFf" class="login-layout">
    <q-page-container>
      <q-page class="login-page">
        <div class="login-shell">
          <section class="login-brand-panel">
            <div class="login-brand-top">
              <div class="login-brand-mark"><BankLogo /></div>
              <span>bembank.</span>
            </div>
            <div class="login-brand-copy">
              <div class="eyebrow">YOUR MONEY. YOUR POSSIBILITIES.</div>
              <h1>A simpler way<br>to move forward.</h1>
              <p>Everyday banking, meaningful goals, and everything in between. All in one place.</p>
              <div class="login-orbit"><BankLogo /></div>
            </div>
            <div class="login-brand-footer">
              <q-icon name="lock" size="16px" />
              <span>Simulated banking · No real money moves</span>
            </div>
          </section>

          <section class="login-form-panel">
            <div class="login-form-content">
              <div class="mobile-login-logo"><BankLogo /></div>
              <div class="eyebrow">Account access</div>
              <h2 class="login-form-title">{{ pinChallenge ? (pinSetup ? 'Create your PIN' : 'Enter your PIN') : challenge ? 'Verify your sign-in' : 'Welcome back' }}</h2>
              <p class="login-form-subtitle">{{ pinChallenge ? (pinSetup ? 'Choose a six-digit PIN for future sign-ins. Confirm it below to continue.' : 'Enter your six-digit PIN to finish signing in.') : challenge ? 'Enter the six-digit code from your authenticator app. Your sign-in request lasts five minutes.' : 'Sign in to your Bembank account' }}</p>

              <q-dialog v-model="recoveryHelp"><q-card style="width:440px;max-width:95vw"><q-card-section><h2 class="section-heading">Recover your account</h2><p>Contact Bembank staff to verify your identity and reset your password. Staff can do this under Help & support → Customer password recovery.</p><p>If you lost your authenticator, use one of your saved recovery codes after entering your password. A password reset does not remove authenticator protection.</p></q-card-section><q-card-actions align="right"><q-btn flat label="Close" v-close-popup /></q-card-actions></q-card></q-dialog>
              <q-form v-if="!challenge && !pinChallenge" @submit="onSubmit" class="column q-gutter-md">
                <q-input v-if="isNativeApp" v-model.trim="serverUrl" label="Server address" type="url" filled hint="Use your laptop's Wi-Fi address; HTTP is for demos only." :rules="[(val) => !!val || 'Server address is required']" />
                <q-input
                  v-model="username"
                  label="Email or Username"
                  hide-bottom-space
                  autocomplete="username"
                  filled
                  autofocus
                  :rules="[(val) => !!val || 'Username is required']"
                />
                <q-input
                  v-model="password"
                  label="Password"
                  hide-bottom-space
                  autocomplete="current-password"
                  filled
                  :type="showPassword ? 'text' : 'password'"
                  :rules="[(val) => !!val || 'Password is required']"
                >
                  <template #append>
                    <q-btn
                      flat
                      dense
                      round
                      :icon="showPassword ? 'visibility' : 'visibility_off'"
                      :aria-label="showPassword ? 'Hide password' : 'Show password'"
                      :title="showPassword ? 'Hide password' : 'Show password'"
                      @click="showPassword = !showPassword"
                    />
                  </template>
                </q-input>

                <div class="login-recovery-row">
                  <q-btn flat no-caps label="Forgot password?" @click="recoveryHelp = true" />
                </div>

                <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9">
                  {{ errorMessage }}
                </q-banner>

                <q-btn
                  type="submit"
                  label="Sign In"
                  icon-right="arrow_forward"
                  color="primary"
                  class="full-width login-submit"
                  :loading="loading"
                  unelevated
                />
              </q-form>
              <q-form v-else-if="challenge" @submit="verifyOtp" class="column q-gutter-md">
                <q-input v-model.trim="otpCode" filled autofocus :label="useRecovery ? 'Recovery code' : 'Authentication code'" :inputmode="useRecovery ? 'text' : 'numeric'" autocomplete="one-time-code" :maxlength="useRecovery ? 32 : 6" :rules="[value => useRecovery ? !!value || 'Enter a recovery code' : /^[0-9]{6}$/.test(value) || 'Enter all six digits']" />
                <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9" role="alert">{{ errorMessage }}</q-banner>
                <q-btn type="submit" color="primary" label="Verify and sign in" :loading="loading" unelevated />
                <q-btn flat :disable="loading" :label="useRecovery ? 'Use authenticator code' : 'Use a recovery code'" @click="useRecovery = !useRecovery; otpCode = ''; errorMessage = ''" />
                <q-btn flat :disable="loading" label="Back to sign in" @click="challenge = ''; otpCode = ''; errorMessage = ''; useRecovery = false" />
              </q-form>
              <q-form v-else @submit="verifyPin" class="column q-gutter-md">
                <q-input v-model="pin" label="Six-digit PIN" type="password" inputmode="numeric" autocomplete="off" maxlength="6" filled autofocus :rules="[value => /^[0-9]{6}$/.test(value) || 'Enter exactly six digits']" />
                <q-input v-if="pinSetup" v-model="confirmPin" label="Confirm PIN" type="password" inputmode="numeric" autocomplete="off" maxlength="6" filled :rules="[value => value === pin || 'PINs must match']" />
                <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9" role="alert">{{ errorMessage }}</q-banner>
                <q-btn type="submit" color="primary" :label="pinSetup ? 'Save PIN and sign in' : 'Verify and sign in'" :loading="loading" unelevated />
                <q-btn flat :disable="loading" label="Back to sign in" @click="pinChallenge = ''; pin = ''; confirmPin = ''; errorMessage = ''" />
              </q-form>
              <template v-if="!challenge && !pinChallenge">
                <p class="login-signup-link">Don't have an account? <router-link to="/signup">Sign up</router-link></p>
              </template>
            </div>
          </section>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import BankLogo from '@/components/BankLogo.vue'
import { isNativeApp, setApiBaseUrl } from '@/services/api'

const serverUrl = ref(localStorage.getItem('bembankApiUrl') || '')
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const challenge = ref('')
const pinChallenge = ref('')
const pinSetup = ref(false)
const pin = ref('')
const confirmPin = ref('')
const otpCode = ref('')
const useRecovery = ref(false)

const auth = useAuthStore()
const router = useRouter()
const recoveryHelp = ref(false)

async function onSubmit () {
  loading.value = true
  errorMessage.value = ''
  try {
    if (isNativeApp) setApiBaseUrl(serverUrl.value)
    const result = await auth.login(username.value, password.value)
    password.value = ''
    if (result.otp_required) challenge.value = result.challenge_token
    else if (result.pin_required) { pinChallenge.value = result.challenge_token; pinSetup.value = result.pin_setup_required }
    else router.push('/')
  } catch (err) {
    if (err.response) {
      // Backend rejected the request (e.g. wrong credentials on /auth/login)
      errorMessage.value = typeof err.response.data?.detail === 'string' && err.response.status < 500 ? err.response.data.detail : 'Sign-in is temporarily unavailable. Please try again.'
    } else if (err.request) {
      // Request never got a response at all: wrong API base URL, backend down, or CORS block
      errorMessage.value = 'We could not connect. Check your connection and try again.'
    } else {
      // Something failed in our own post-login logic (e.g. no matching user record)
      errorMessage.value = err.message || 'Login failed for an unknown reason.'
    }
  } finally {
    loading.value = false
  }
}

async function verifyOtp () {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await auth.verifyOtp(challenge.value, otpCode.value)
    challenge.value = ''; otpCode.value = ''
    pinChallenge.value = result.challenge_token
    pinSetup.value = result.pin_setup_required
  } catch (error) {
    errorMessage.value = typeof error.response?.data?.detail === 'string' && error.response.status < 500 ? error.response.data.detail : 'Verification could not be completed. Please try again.'
  } finally { loading.value = false }
}
async function verifyPin () {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.verifyPin(pinChallenge.value, pin.value, pinSetup.value ? confirmPin.value : undefined)
    pin.value = ''; confirmPin.value = ''; pinChallenge.value = ''
    router.replace('/')
  } catch (error) {
    errorMessage.value = typeof error.response?.data?.detail === 'string' && error.response.status < 500 ? error.response.data.detail : 'PIN verification could not be completed. Please try again.'
    pin.value = ''; confirmPin.value = ''
  } finally { loading.value = false }
}
</script>
