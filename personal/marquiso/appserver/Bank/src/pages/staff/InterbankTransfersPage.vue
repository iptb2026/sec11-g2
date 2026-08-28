<template><StaffTablePage title="Interbank transfers" description="Review external transfer operations." endpoint="/interbank-transfers/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'id', label: 'ID', field: 'id' }, { name: 'source_account_id', label: 'Source', field: 'source_account_id' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'transfer_fee', label: 'Transfer fee', field: 'transfer_fee' }, { name: 'status', label: 'Status', field: 'status' }]
</script>
