<template><ManagerTablePage title="Manager dashboard" description="Branch overview and managed account balances." endpoint="/accounts/" :columns="columns" /></template>
<script setup>
import ManagerTablePage from './ManagerTablePage.vue'
const columns = [{ name: 'account_number', label: 'Account', field: 'account_number', align: 'left' }, { name: 'customer_id', label: 'Customer', field: 'customer_id' }, { name: 'available_balance', label: 'Available balance', field: 'available_balance' }, { name: 'status', label: 'Status', field: 'status' }]
</script>
