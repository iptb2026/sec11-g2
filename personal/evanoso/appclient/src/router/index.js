import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginPage from '../pages/LoginPage.vue'

// Admin pages
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminDashboard from '../pages/admin/DashboardPage.vue'
import AdminUsers from '../pages/admin/UsersPage.vue'
import AdminRoles from '../pages/admin/RolesPage.vue'
import AdminBanks from '../pages/admin/BanksPage.vue'
import AdminAccountTypes from '../pages/admin/AccountTypesPage.vue'
import AdminFeeTypes from '../pages/admin/FeeTypesPage.vue'
import AdminAccounts from '../pages/admin/AccountsPage.vue'
import AdminSessions from '../pages/admin/SessionsPage.vue'
import AdminAuditLogs from '../pages/admin/AuditLogsPage.vue'

// Staff pages
import StaffLayout from '../layouts/StaffLayout.vue'
import StaffDashboard from '../pages/staff/DashboardPage.vue'
import StaffAccounts from '../pages/staff/AccountsPage.vue'
import StaffDeposits from '../pages/staff/DepositsPage.vue'
import StaffWithdrawals from '../pages/staff/WithdrawalsPage.vue'

// Customer pages
import CustomerLayout from '../layouts/CustomerLayout.vue'
import CustomerDashboard from '../pages/customer/DashboardPage.vue'
import CustomerAccounts from '../pages/customer/AccountsPage.vue'
import CustomerTransactions from '../pages/customer/TransactionsPage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginPage, meta: { public: true } },

  // Admin routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'ADMIN' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'users', name: 'AdminUsers', component: AdminUsers },
      { path: 'roles', name: 'AdminRoles', component: AdminRoles },
      { path: 'banks', name: 'AdminBanks', component: AdminBanks },
      { path: 'account-types', name: 'AdminAccountTypes', component: AdminAccountTypes },
      { path: 'fee-types', name: 'AdminFeeTypes', component: AdminFeeTypes },
      { path: 'accounts', name: 'AdminAccounts', component: AdminAccounts },
      { path: 'sessions', name: 'AdminSessions', component: AdminSessions },
      { path: 'audit-logs', name: 'AdminAuditLogs', component: AdminAuditLogs },
    ],
  },

  // Staff routes
  {
    path: '/staff',
    component: StaffLayout,
    meta: { requiresAuth: true, role: 'STAFF' },
    children: [
      { path: '', redirect: '/staff/dashboard' },
      { path: 'dashboard', name: 'StaffDashboard', component: StaffDashboard },
      { path: 'accounts', name: 'StaffAccounts', component: StaffAccounts },
      { path: 'deposits', name: 'StaffDeposits', component: StaffDeposits },
      { path: 'withdrawals', name: 'StaffWithdrawals', component: StaffWithdrawals },
    ],
  },

  // Customer routes
  {
    path: '/customer',
    component: CustomerLayout,
    meta: { requiresAuth: true, role: 'CUSTOMER' },
    children: [
      { path: '', redirect: '/customer/dashboard' },
      { path: 'dashboard', name: 'CustomerDashboard', component: CustomerDashboard },
      { path: 'accounts', name: 'CustomerAccounts', component: CustomerAccounts },
      { path: 'transactions', name: 'CustomerTransactions', component: CustomerTransactions },
    ],
  },

  // Catch-all
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // Public routes
  if (to.meta.public) {
    if (auth.isAuthenticated && to.name === 'Login') {
      // Already logged in — redirect to appropriate dashboard
      const role = auth.roleCode
      if (role === 'ADMIN') return next('/admin/dashboard')
      if (role === 'STAFF') return next('/staff/dashboard')
      if (role === 'CUSTOMER') return next('/customer/dashboard')
    }
    return next()
  }

  // Auth required
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  // Role check
  if (to.meta.role && auth.roleCode !== to.meta.role) {
    // Redirect to correct dashboard instead of showing forbidden
    const role = auth.roleCode
    if (role === 'ADMIN') return next('/admin/dashboard')
    if (role === 'STAFF') return next('/staff/dashboard')
    if (role === 'CUSTOMER') return next('/customer/dashboard')
    return next('/login')
  }

  next()
})

export default router
