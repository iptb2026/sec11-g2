<template>
  <div>
    <q-input :model-value="modelValue" :label="label" filled :type="visible ? 'text' : 'password'" autocomplete="new-password" :rules="[passwordRule]" @update:model-value="$emit('update:modelValue', $event)">
      <template #append><q-btn flat round dense :icon="visible ? 'visibility_off' : 'visibility'" :aria-label="visible ? 'Hide password' : 'Show password'" @click="visible = !visible" /></template>
    </q-input>
    <ul class="password-requirements" aria-label="Password requirements"><li v-for="check in checks" :key="check.label" :class="{ met: check.met }"><q-icon :name="check.met ? 'check_circle' : 'radio_button_unchecked'" /><span>{{ check.label }}</span><span class="sr-only">{{ check.met ? ' — met' : ' — not met' }}</span></li></ul>
  </div>
</template>
<script setup>
import { computed, ref } from 'vue'
import { passwordChecks, passwordRule } from '@/utils/password-policy'
const props = defineProps({ modelValue: { type: String, default: '' }, label: { type: String, default: 'Password' } })
defineEmits(['update:modelValue'])
const visible = ref(false), checks = computed(() => passwordChecks(props.modelValue))
</script>
<style scoped>
.password-requirements { list-style: none; padding: 0; margin: 0 0 16px; color: #9cafc9; font-size: 12px; }
.password-requirements li { display: flex; align-items: center; gap: 7px; margin: 5px 0; }
.password-requirements .met { color: #77d9b7; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
</style>
