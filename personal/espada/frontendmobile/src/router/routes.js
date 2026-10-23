import MainLayout from 'src/layouts/MainLayout.vue'

export default [
  { path: '/login', component: () => import('src/pages/LoginPage.vue') },
  {
    path: '/', component: MainLayout, meta: { requiresAuth: true }, children: [
      { path: '', component: () => import('src/pages/DashboardPage.vue') },
      { path: 'account', component: () => import('src/pages/AccountPage.vue') },
      { path: 'transactions', component: () => import('src/pages/TransactionsPage.vue') },
    ],
  },
  { path: '/:catchAll(.*)*', redirect: '/login' },
]
