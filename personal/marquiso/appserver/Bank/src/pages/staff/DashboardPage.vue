<template><StaffTablePage title="Staff dashboard" description="Daily operational activity overview." endpoint="/deposits/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'id', label: 'ID', field: 'id' }, { name: 'account_id', label: 'Account', field: 'account_id' }, { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel' }]
</script>
