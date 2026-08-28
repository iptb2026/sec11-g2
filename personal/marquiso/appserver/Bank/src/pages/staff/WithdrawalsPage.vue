<template><StaffTablePage title="Withdrawals" description="Process and review customer withdrawals." endpoint="/withdrawals/" :columns="columns" /></template>
<script setup>
import StaffTablePage from './StaffTablePage.vue'
const columns = [{ name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' }, { name: 'account_id', label: 'Account', field: 'account_id' }, { name: 'amount', label: 'Amount', field: 'amount' }, { name: 'withdrawal_channel', label: 'Channel', field: 'withdrawal_channel' }, { name: 'transaction_date', label: 'Date', field: 'transaction_date' }]
</script>
