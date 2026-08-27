const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { public: true },
    children: [{ path: '', component: () => import('@/pages/LoginPage.vue') }]
  },
  {
    path: '/register',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { public: true },
    children: [{ path: '', component: () => import('@/pages/RegisterPage.vue') }]
  },

  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: () => import('@/pages/IndexPage.vue') },

      // Admin
      { path: 'admin/dashboard', component: () => import('@/pages/admin/AdminDashboard.vue'), meta: { roles: ['admin'] } },
      { path: 'admin/users', component: () => import('@/pages/admin/UsersPage.vue'), meta: { roles: ['admin'] } },

      // Staff
      { path: 'staff/dashboard', component: () => import('@/pages/staff/StaffDashboard.vue'), meta: { roles: ['staff', 'admin'] } },
      { path: 'staff/customers', component: () => import('@/pages/staff/CustomersPage.vue'), meta: { roles: ['staff', 'admin'] } },

      // Customer
      { path: 'customer/dashboard', component: () => import('@/pages/customer/CustomerDashboard.vue'), meta: { roles: ['customer'] } },
      { path: 'customer/profile', component: () => import('@/pages/customer/ProfilePage.vue'), meta: { roles: ['customer', 'staff', 'admin'] } },

      { path: 'access-denied', component: () => import('@/components/AccessDenied.vue'), meta: { public: true } },
    ]
  },

  // Fallback
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
