<template>
  <q-layout view="lHh Lpr lFf" class="login-layout">
    <q-page-container><q-page class="login-page signup-page">
      <div class="login-shell">
        <section class="login-brand-panel">
          <div class="login-brand-top"><div class="login-brand-mark"><BankLogo /></div><span>bembank.</span></div>
          <div class="login-brand-copy"><div class="eyebrow">YOUR MONEY. YOUR POSSIBILITIES.</div><h1>A simpler way<br>to move forward.</h1><p>Everyday banking, meaningful goals, and everything in between. All in one place.</p><div class="login-orbit"><BankLogo /></div></div>
          <div class="login-brand-footer"><q-icon name="lock" size="16px" /><span>Simulated banking · No real money moves</span></div>
        </section>
        <section class="login-form-panel"><div class="login-form-content">
          <div class="mobile-login-logo"><BankLogo /></div>
          <div class="eyebrow">Account access</div>
          <h1 class="login-form-title">{{ created ? 'You’re all set' : 'Create your account' }}</h1>
          <template v-if="created">
            <p class="login-form-subtitle">Your customer login and savings account are ready. Sign in to create your six-digit PIN.</p>
            <q-btn to="/login" label="Continue to sign in" color="primary" class="full-width login-submit" unelevated />
          </template>
          <template v-else>
            <p class="login-form-subtitle">Start with a free, zero-balance savings account.</p>
            <q-form class="signup-form column q-gutter-md" @submit="submit">
              <q-input v-model.trim="form.first_name" label="First name" autocomplete="given-name" maxlength="100" filled hide-bottom-space :rules="[required]" />
              <q-input v-model.trim="form.last_name" label="Last name" autocomplete="family-name" maxlength="100" filled hide-bottom-space :rules="[required]" />
              <q-input v-model.trim="form.username" label="Username" autocomplete="username" maxlength="50" filled hide-bottom-space :rules="[v => /^[a-zA-Z0-9_.-]{3,50}$/.test(v) || 'Use 3–50 letters, numbers, dots, dashes or underscores']" />
              <q-input v-model.trim="form.email" label="Email" type="email" autocomplete="email" maxlength="150" filled hide-bottom-space :rules="[required]" />
              <NewPasswordField v-model="form.password" />
              <q-input v-model="confirmation" label="Confirm password" type="password" autocomplete="new-password" filled hide-bottom-space :rules="[v => v === form.password || 'Passwords must match']" />
              <q-banner v-if="error" class="bg-red-1 text-red-9" role="alert">{{ error }}</q-banner>
              <q-btn type="submit" label="Sign up" color="primary" :loading="busy" class="full-width login-submit" unelevated />
            </q-form>
            <p class="login-signup-link">Already have an account? <router-link to="/login">Sign in</router-link></p>
            <p class="signup-demo-note">Simulated banking · No real money moves</p>
          </template>
        </div></section>
      </div>
    </q-page></q-page-container>
  </q-layout>
</template>
<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import BankLogo from '@/components/BankLogo.vue'
import NewPasswordField from '@/components/NewPasswordField.vue'
const form = ref({ first_name: '', last_name: '', username: '', email: '', password: '' })
const confirmation = ref(''), error = ref(''), busy = ref(false), created = ref(false)
const required = value => !!value || 'This field is required'
async function submit () {
  if (busy.value) return
  busy.value = true; error.value = ''
  try {
    await api.post('/auth/signup', form.value)
    form.value.password = ''; confirmation.value = ''; created.value = true
  } catch (e) {
    error.value = typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Could not create your account. Please try again.'
  } finally { busy.value = false }
}
</script>
