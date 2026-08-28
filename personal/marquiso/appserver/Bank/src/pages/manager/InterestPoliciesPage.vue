<template><ManagerTablePage title="Interest policies" description="Review interest policy configuration." endpoint="/interest-policies/" :columns="columns" /></template>
<script setup>
import ManagerTablePage from './ManagerTablePage.vue'
const columns = [{ name: 'id', label: 'ID', field: 'id' }, { name: 'account_type_id', label: 'Account type', field: 'account_type_id' }, { name: 'annual_interest_rate', label: 'Annual rate', field: 'annual_interest_rate' }]
</script>
