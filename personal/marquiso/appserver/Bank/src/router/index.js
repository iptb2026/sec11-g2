import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import routes from './routes.js'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
  })

  Router.beforeEach((to) => {
    const persisted = localStorage.getItem('marquiso-auth')
    let isAuthenticated = false

    try {
      isAuthenticated = Boolean(persisted && JSON.parse(persisted).token)
    } catch {
      localStorage.removeItem('marquiso-auth')
    }

    if (to.meta.requiresAuth && !isAuthenticated) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }

    if (to.meta.guestOnly && isAuthenticated) {
      return '/'
    }

    if (to.meta.managerAccess) {
      const role = persisted ? JSON.parse(persisted).roleCode : null
      if (!['ADMIN', 'MANAGER'].includes(role)) return '/'
    }

    if (to.meta.staffAccess) {
      const role = persisted ? JSON.parse(persisted).roleCode : null
      if (!['ADMIN', 'STAFF'].includes(role)) return '/'
    }

    if (to.meta.adminAccess) {
      const role = persisted ? JSON.parse(persisted).roleCode : null
      if (role !== 'ADMIN') return '/'
    }
  })

  return Router
})
