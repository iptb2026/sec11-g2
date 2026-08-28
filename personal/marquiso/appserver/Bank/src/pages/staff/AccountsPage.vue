<template><StaffTablePage title="Accounts" description="Review customer accounts for service operations." endpoint="/accounts/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'account_number', label: 'Account number', field: 'account_number', align: 'left' }, { name: 'customer_id', label: 'Customer', field: 'customer_id' }, { name: 'available_balance', label: 'Available', field: 'available_balance' }, { name: 'status', label: 'Status', field: 'status' }]
</script>
