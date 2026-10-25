<template>
  <q-input v-bind="$attrs" :model-value="modelValue" :label="label" filled readonly class="date-picker-field" @click="open = true" @keydown.enter.prevent="open = true" @keydown.space.prevent="open = true">
    <template #append><q-btn flat round dense icon="event" :aria-label="`Choose ${label}`" @click.stop="open = true" /></template>
  </q-input>
  <q-dialog v-model="open">
    <q-card class="date-picker-dialog">
      <q-date :model-value="modelValue || null" mask="YYYY-MM-DD" :title="label" :default-year-month="defaultMonth" today-btn @update:model-value="choose" />
      <q-card-actions align="right"><q-btn v-if="clearable" flat label="Clear date" @click="choose(null)" /><q-btn flat label="Close" v-close-popup /></q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script setup>
import { computed, ref } from 'vue'
defineOptions({ inheritAttrs: false })
const props = defineProps({ modelValue: { type: String, default: null }, label: { type: String, default: 'Date' }, clearable: { type: Boolean, default: false } })
const emit = defineEmits(['update:modelValue'])
const open = ref(false)
const defaultMonth = computed(() => props.modelValue ? props.modelValue.slice(0,7).replace('-', '/') : undefined)
function choose(value) { emit('update:modelValue', value); open.value = false }
</script>
<style scoped>
.date-picker-field :deep(input) { cursor: pointer; }
.date-picker-dialog { max-width: 95vw; }
.date-picker-dialog :deep(.q-date) { box-shadow: none; max-width: 100%; }
</style>
