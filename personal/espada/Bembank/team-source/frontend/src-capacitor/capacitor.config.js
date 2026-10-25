const { defineCapacitorConfig } = require('@quasar/app-vite/capacitor');

module.exports = defineCapacitorConfig({
  appId: 'com.bembank.app',
  appName: 'Bembank',
  server: { androidScheme: 'http' }
});
