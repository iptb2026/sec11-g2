const layer1 = [
  { path: 'roles', component: () => import('src/pages/admin/ResourcePage.vue'), meta: { title: 'Roles', endpoint: '/roles/', resource: 'roles', roles: ['ADMIN'] } },
  { path: 'account-types', component: () => import('src/pages/admin/ResourcePage.vue'), meta: { title: 'Account Types', endpoint: '/account-types/', resource: 'accountTypes', roles: ['ADMIN'] } },
  { path: 'banks', component: () => import('src/pages/admin/ResourcePage.vue'), meta: { title: 'Banks', endpoint: '/banks/', resource: 'banks', roles: ['ADMIN'] } },
  { path: 'fee-types', component: () => import('src/pages/admin/ResourcePage.vue'), meta: { title: 'Fee Types', endpoint: '/fee-types/', resource: 'feeTypes', roles: ['ADMIN'] } }
]
const shell = (path, title, endpoint, roles = ['ADMIN', 'STAFF'], group = 'BANKING OPERATIONS') => ({ path, component: () => import('src/pages/BankingResourcePage.vue'), meta: { title, endpoint, roles, group } })

export default [
  { path: '/login', component: () => import('src/pages/LoginPage.vue') },
  { path: '/', component: () => import('src/layouts/MainLayout.vue'), meta: { requiresAuth: true }, children: [
    { path: '', component: () => import('src/pages/DashboardPage.vue'), meta: { title: 'Dashboard' } },
    ...layer1,
    shell('users', 'Users', '/users/', ['ADMIN'], 'IDENTITY & ACCESS'), shell('audit-logs', 'Audit Logs', '/audit-logs/', ['ADMIN'], 'IDENTITY & ACCESS'),
    shell('accounts', 'Accounts', '/accounts/'), shell('withdrawal-limits', 'Withdrawal Limits', '/withdrawal-limits/'), shell('interest-policies', 'Interest Policies', '/interest-policies/'),
    shell('deposits', 'Deposits', '/deposits/'), shell('withdrawals', 'Withdrawals', '/withdrawals/'), shell('transfers', 'Transfers', '/transfers/'), shell('interbank-transfers', 'Interbank Transfers', '/interbank-transfers/'),
    shell('fee-records', 'Fee Records', '/fee-records/'), shell('interest-records', 'Interest Records', '/interest-records/'), shell('ledger-entries', 'Ledger Entries', '/ledger-entries/'),
    shell('my-account', 'My Account', '/accounts/', ['CUSTOMER'], 'CUSTOMER SELF-SERVICE'), shell('my-transactions', 'My Transactions', '/deposits/', ['CUSTOMER'], 'CUSTOMER SELF-SERVICE')
  ]},
  { path: '/:catchAll(.*)*', component: () => import('src/pages/ErrorNotFound.vue') }
]
