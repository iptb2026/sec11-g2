<template><q-page class="page"><div class="eyebrow">{{ route.meta.title }}</div><h1>{{ route.meta.title }}</h1><q-banner rounded class="notice"><q-icon name="construction" size="24px" /> This workspace is reserved for the next backend layer. The route and role guard are ready.</q-banner></q-page></template>
<script setup>import { useRoute } from 'vue-router'; const route = useRoute()</script>
