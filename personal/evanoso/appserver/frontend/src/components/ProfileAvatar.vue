<template><q-avatar :size="size" class="header-avatar"><img v-if="auth.profilePhoto" :src="auth.profilePhoto" alt="Profile photo" style="object-fit:cover" /><span v-else>{{ initials }}</span></q-avatar></template>
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth-store'
defineProps({ size: { type: String, default: '40px' } })
const auth = useAuthStore()
const initials = computed(() => (auth.fullName || auth.username || 'U').split(/\s+/).slice(0, 2).map(s => s[0]).join('').toUpperCase())
</script>
