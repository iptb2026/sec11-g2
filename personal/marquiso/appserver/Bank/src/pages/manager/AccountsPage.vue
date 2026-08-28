<template><ManagerTablePage title="Accounts" description="Review customer account balances and status." endpoint="/accounts/" :columns="columns" /></template>
<script setup>
import ManagerTablePage from './ManagerTablePage.vue'
const columns = [{ name: 'account_number', label: 'Account number', field: 'account_number', align: 'left' }, { name: 'customer_id', label: 'Customer', field: 'customer_id' }, { name: 'account_type_id', label: 'Account type', field: 'account_type_id' }, { name: 'available_balance', label: 'Available', field: 'available_balance' }, { name: 'ledger_balance', label: 'Ledger', field: 'ledger_balance' }, { name: 'status', label: 'Status', field: 'status' }]
</script>
