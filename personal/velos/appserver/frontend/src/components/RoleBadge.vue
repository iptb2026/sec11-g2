<template>
  <q-badge :color="color" class="q-ml-sm">
    <div class="row items-center q-pa-xs">
      <q-icon name="verified_user" size="16px" />
      <div class="q-ml-xs text-caption">{{ role.toUpperCase() }}</div>
    </div>
  </q-badge>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ role: { type: String, required: true } })
const color = computed(() => props.role === 'admin' ? 'deep-purple' : props.role === 'staff' ? 'blue' : 'teal')
</script>
