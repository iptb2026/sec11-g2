<template><ManagerTablePage title="Ledger entries" description="Review the financial ledger." endpoint="/ledger-entries/" :columns="columns" /></template>
<script setup>
import ManagerTablePage from './ManagerTablePage.vue'
const columns = [{ name: 'id', label: 'ID', field: 'id' }, { name: 'account_id', label: 'Account', field: 'account_id' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'entry_type', label: 'Entry type', field: 'entry_type' }]
</script>
