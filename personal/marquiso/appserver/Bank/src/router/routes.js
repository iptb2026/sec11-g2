const routes = [
  {
    path: '/login',
    meta: { guestOnly: true },
    component: () => import('@/pages/LoginPage.vue')
  },
  {
    path: '/',
    meta: { requiresAuth: true },
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('@/pages/IndexPage.vue') },
      { path: 'admin/users', meta: { adminAccess: true }, component: () => import('@/pages/admin/UsersPage.vue') },
      { path: 'manager/dashboard', meta: { managerAccess: true }, component: () => import('@/pages/manager/DashboardPage.vue') },
      { path: 'manager/accounts', meta: { managerAccess: true }, component: () => import('@/pages/manager/AccountsPage.vue') },
      { path: 'manager/transactions', meta: { managerAccess: true }, component: () => import('@/pages/manager/TransactionsPage.vue') },
      { path: 'manager/transfers', meta: { managerAccess: true }, component: () => import('@/pages/manager/TransfersPage.vue') },
      { path: 'manager/interbank-transfers', meta: { managerAccess: true }, component: () => import('@/pages/manager/InterbankTransfersPage.vue') },
      { path: 'manager/interest-policies', meta: { managerAccess: true }, component: () => import('@/pages/manager/InterestPoliciesPage.vue') },
      { path: 'manager/fee-records', meta: { managerAccess: true }, component: () => import('@/pages/manager/FeeRecordsPage.vue') },
      { path: 'manager/ledger-entries', meta: { managerAccess: true }, component: () => import('@/pages/manager/LedgerEntriesPage.vue') },
      { path: 'staff/dashboard', meta: { staffAccess: true }, component: () => import('@/pages/staff/DashboardPage.vue') },
      { path: 'staff/accounts', meta: { staffAccess: true }, component: () => import('@/pages/staff/AccountsPage.vue') },
      { path: 'staff/deposits', meta: { staffAccess: true }, component: () => import('@/pages/staff/DepositsPage.vue') },
      { path: 'staff/withdrawals', meta: { staffAccess: true }, component: () => import('@/pages/staff/WithdrawalsPage.vue') },
      { path: 'staff/transfers', meta: { staffAccess: true }, component: () => import('@/pages/staff/TransfersPage.vue') },
      { path: 'staff/interbank-transfers', meta: { staffAccess: true }, component: () => import('@/pages/staff/InterbankTransfersPage.vue') },
      { path: 'second', component: () => import('@/pages/SecondPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
