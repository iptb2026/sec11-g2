<template>
  <div class="q-pa-md flex flex-center" style="min-height:160px">
    <div class="text-center">
      <div class="text-h6">{{ title }}</div>
      <div class="text-subtitle2 q-mt-sm">{{ description }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ title: { type: String, default: 'No items' }, description: { type: String, default: 'There are no items to show.' } })
</script>
