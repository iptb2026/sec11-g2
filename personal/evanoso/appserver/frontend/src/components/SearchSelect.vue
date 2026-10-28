<template>
  <q-select
    v-bind="$attrs"
    :options="visibleOptions"
    :input-value="searchText"
    use-input
    input-debounce="0"
    @filter="onFilter"
    @input-value="searchText = $event"
    @clear="clearSearch"
    @popup-hide="clearSearch"
  >
    <template v-for="(_, name) in $slots" #[name]="scope">
      <slot :name="name" v-bind="scope || {}" />
    </template>
    <template #no-option>
      <q-item><q-item-section class="text-grey-7">No matching records</q-item-section></q-item>
    </template>
  </q-select>
</template>

<script setup>
import { ref, watch } from 'vue'
import { filterOptions } from '@/utils/filter-options'

defineOptions({ inheritAttrs: false })
const props = defineProps({ options: { type: Array, default: () => [] } })
const visibleOptions = ref([])
const searchText = ref('')

watch(() => props.options, options => { visibleOptions.value = options }, { immediate: true })

function onFilter (query, update) {
  update(() => { visibleOptions.value = filterOptions(props.options, query) })
}

function clearSearch () {
  searchText.value = ''
  visibleOptions.value = props.options
}
</script>
