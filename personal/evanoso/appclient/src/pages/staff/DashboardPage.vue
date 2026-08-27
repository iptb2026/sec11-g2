<template>
  <div>
    <div class="text-h5 q-mb-md text-weight-bold">Staff Dashboard</div>
    <div class="row q-gutter-md">
      <q-card v-for="card in cards" :key="card.label" class="col-12 col-sm-5 col-md-3" flat bordered>
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon :name="card.icon" size="40px" :color="card.color" />
          <div>
            <div class="text-h6">{{ card.count }}</div>
            <div class="text-caption text-grey">{{ card.label }}</div>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
const cards = ref([
  { label:'Accounts',icon:'account_box',color:'teal',count:'...' },
  { label:'Deposits',icon:'savings',color:'green',count:'...' },
  { label:'Withdrawals',icon:'money_off',color:'orange',count:'...' },
])
onMounted(async () => {
  try {
    const [a, d, w] = await Promise.all([api.get('/accounts/'), api.get('/deposits/'), api.get('/withdrawals/')])
    cards.value[0].count = a.data.length
    cards.value[1].count = d.data.length
    cards.value[2].count = w.data.length
  } catch(e) {}
})
</script>
