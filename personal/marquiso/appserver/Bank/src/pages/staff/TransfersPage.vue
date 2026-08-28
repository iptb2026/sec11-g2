<template><StaffTablePage title="Transfers" description="Review internal customer transfer activity." endpoint="/transfers/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'transfer_reference', label: 'Reference', field: 'transfer_reference', align: 'left' }, { name: 'source_account_id', label: 'From', field: 'source_account_id' }, { name: 'destination_account_id', label: 'To', field: 'destination_account_id' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'status', label: 'Status', field: 'status' }]
</script>
