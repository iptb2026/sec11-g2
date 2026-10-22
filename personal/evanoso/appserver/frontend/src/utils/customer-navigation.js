export const customerActionGroups = [
  { label: 'Move money', items: [
    { label: 'Send funds', icon: 'swap_horiz', to: '/customer/transfers' },
    { label: 'Scan QR', icon: 'qr_code_scanner', to: '/customer/transfers?scan=1' },
    { label: 'Deposit / withdraw', icon: 'payments', to: '/requests' },
    { label: 'Other banks', icon: 'account_balance', to: '/customer/other-banks' },
    { label: 'Pay bills', icon: 'receipt_long', to: '/customer/bill-payments' },
    { label: 'Buy load', icon: 'phone_android', to: '/customer/mobile-load' },
  ] },
  { label: 'Manage your money', items: [
    { label: 'My account', icon: 'account_balance_wallet', to: '/my-account' },
    { label: 'My cards', icon: 'credit_card', to: '/customer/cards' },
    { label: 'Savings goals', icon: 'savings', to: '/customer/savings' },
    { label: 'Investments', icon: 'trending_up', to: '/customer/investments' },
    { label: 'Transactions', icon: 'history', to: '/my-transactions' },
    { label: 'Statements', icon: 'description', to: '/statements' },
  ] },
  { label: 'Settings & support', items: [
    { label: 'Activity alerts', icon: 'notifications_none', to: '/customer/notifications' },
    { label: 'Profile & security', icon: 'manage_accounts', to: '/profile' },
    { label: 'Help & support', icon: 'help_outline', to: '/help' },
  ] },
]
