import { route } from 'quasar/wrappers'
import { createRouter, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'src/stores/auth-store'

export default route(function () {
  const router = createRouter({ history: createWebHashHistory(), routes, scrollBehavior: () => ({ left: 0, top: 0 }) })
  router.beforeEach((to) => {
    const auth = useAuthStore()
    if (to.path === '/login' && auth.isAuthenticated) return '/'
    if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
    if (to.meta.roles && !to.meta.roles.includes(auth.roleCode)) return '/'
  })
  return router
})
