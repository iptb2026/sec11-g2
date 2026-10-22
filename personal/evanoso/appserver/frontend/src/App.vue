<template>
  <MobileStartup><router-view /></MobileStartup>
</template>
<script setup>
import { useQuasar } from 'quasar'
import MobileStartup from '@/components/MobileStartup.vue'
useQuasar().dark.set(true)
</script>
