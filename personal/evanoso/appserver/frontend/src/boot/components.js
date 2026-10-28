import { defineBoot } from '#q-app'
import SearchSelect from '@/components/SearchSelect.vue'

export default defineBoot(({ app }) => {
  app.component('SearchSelect', SearchSelect)
})
