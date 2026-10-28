const routes = [
  { path: '/signup', component: () => import('@/pages/SignupPage.vue') },
  {
    path: '/login',
    component: () => import('@/pages/LoginPage.vue'),
  },

  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
      { path: 'staff/register', component: () => import('@/pages/RegistrationPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'statements', component: () => import('@/pages/StatementsPage.vue') },
      { path: 'customer/other-banks', component: () => import('@/pages/customer/OtherBankPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'help', component: () => import('@/pages/HelpPage.vue') },
      { path: 'profile', component: () => import('@/pages/ProfilePage.vue') },
      { path: 'requests', component: () => import('@/pages/RequestsPage.vue') },
      { path: 'customer/cards', component: () => import('@/pages/customer/CardsPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'customer/notifications', component: () => import('@/pages/customer/NotificationsPage.vue'), meta: { roles: ['CUSTOMER'] } },

      // --- ADMIN: system configuration ---
      { path: 'admin/roles', component: () => import('@/pages/admin/RolesPage.vue'), meta: { roles: ['ADMIN'] } },
      { path: 'admin/account-types', component: () => import('@/pages/admin/AccountTypesPage.vue'), meta: { roles: ['ADMIN'] } },
      { path: 'admin/banks', component: () => import('@/pages/admin/BanksPage.vue'), meta: { roles: ['ADMIN'] } },
      { path: 'admin/fee-types', component: () => import('@/pages/admin/FeeTypesPage.vue'), meta: { roles: ['ADMIN'] } },
      { path: 'admin/users', component: () => import('@/pages/admin/UsersPage.vue'), meta: { roles: ['ADMIN'] } },
      { path: 'admin/audit-logs', component: () => import('@/pages/admin/AuditLogsPage.vue'), meta: { roles: ['ADMIN'] } },

      // --- ADMIN + STAFF: day-to-day banking operations ---
      { path: 'accounts', component: () => import('@/pages/staff/AccountsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'withdrawal-limits', component: () => import('@/pages/staff/WithdrawalLimitsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'interest-policies', component: () => import('@/pages/staff/InterestPoliciesPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'deposits', component: () => import('@/pages/staff/DepositsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'withdrawals', component: () => import('@/pages/staff/WithdrawalsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'transfers', component: () => import('@/pages/staff/TransfersPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'interbank-transfers', component: () => import('@/pages/staff/InterbankTransfersPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'fee-records', component: () => import('@/pages/staff/FeeRecordsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'interest-records', component: () => import('@/pages/staff/InterestRecordsPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },
      { path: 'ledger-entries', component: () => import('@/pages/staff/LedgerEntriesPage.vue'), meta: { roles: ['ADMIN', 'STAFF'] } },

      // --- CUSTOMER: self-service ---
      { path: 'my-account', component: () => import('@/pages/customer/MyAccountPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'my-transactions', component: () => import('@/pages/customer/MyTransactionsPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'customer/transfers', component: () => import('@/pages/customer/CustomerTransfersPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'customer/bill-payments', component: () => import('@/pages/customer/BillPaymentsPage.vue'), meta: { roles: ['CUSTOMER'] } },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue'),
  }
]

export default routes
