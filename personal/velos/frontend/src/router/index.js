import { route } from 'quasar/wrappers'
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

export default route((/* { store, ssrContext } */) => {
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

  // Global guard: protect routes using token and backend /users/me
  // Use the new return-based navigation guards (avoid deprecated `next()` callback)
  Router.beforeEach(async (to, from) => {
    const publicRoute = to.meta?.public
    if (publicRoute) return true

    const token = localStorage.getItem('auth_token')
    if (!token) return '/login'

    // If roles required, verify with backend
    if (to.meta?.roles) {
      try {
        const { me } = await import('@/services/authService')
        const user = await me()
        if (!to.meta.roles.includes(user.role_code)) return '/access-denied'
        return true
      } catch (err) {
        return '/login'
      }
    }

    return true
  })

  return Router
})
