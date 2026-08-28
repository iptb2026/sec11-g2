<template><ManagerTablePage title="Fee records" description="Review posted account fees." endpoint="/fee-records/" :columns="columns" /></template>
<script setup>
import ManagerTablePage from './ManagerTablePage.vue'
const columns = [{ name: 'id', label: 'ID', field: 'id' }, { name: 'account_id', label: 'Account', field: 'account_id' }, { name: 'fee_type_id', label: 'Fee type', field: 'fee_type_id' }, { name: 'transaction_reference', label: 'Transaction', field: 'transaction_reference' }, { name: 'amount_charged', label: 'Fee charged', field: 'amount_charged' }, { name: 'charged_at', label: 'Charged at', field: 'charged_at' }]
</script>
