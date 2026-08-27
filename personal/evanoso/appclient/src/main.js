import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog, Loading } from 'quasar'
import router from './router'
import App from './App.vue'

// Quasar CSS
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

// App CSS
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Quasar, {
  plugins: { Notify, Dialog, Loading },
  config: {
    notify: { position: 'top-right', timeout: 3000 },
  },
})

app.mount('#app')
