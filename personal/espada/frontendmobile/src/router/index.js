import { defineRouter } from '#q-app/wrappers'
import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import routes from './routes.js'

export default defineRouter(() => {
  const router = createRouter({
    history: import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
      : createWebHashHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE),
    routes,
  })
  router.beforeEach(to => {
    if (to.meta.requiresAuth && !localStorage.getItem('token')) return '/login'
    if (to.path === '/login' && localStorage.getItem('token')) return '/'
  })
  return router
})
