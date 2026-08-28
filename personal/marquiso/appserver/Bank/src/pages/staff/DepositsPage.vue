<template><StaffTablePage title="Deposits" description="Process and review incoming customer funds." endpoint="/deposits/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' }, { name: 'account_id', label: 'Account', field: 'account_id' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel' }, { name: 'transaction_date', label: 'Date', field: 'transaction_date' }]
</script>
