<template>
  <div class="customer-action-groups">
    <section v-for="group in customerActionGroups" :key="group.label" class="customer-action-group" :aria-label="group.label">
      <h3>{{ group.label }}</h3>
      <div class="customer-action-grid">
        <q-btn v-for="item in group.items" :key="item.to" flat stack no-caps :icon="item.icon" :label="item.label" :to="item.to" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { customerActionGroups } from '@/utils/customer-navigation'
</script>
