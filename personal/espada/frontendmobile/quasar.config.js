import { defineConfig } from '#q-app/wrappers'

export default defineConfig(() => ({
  boot: ['axios'],
  css: ['app.css'],
  extras: ['material-icons'],
  framework: { plugins: ['Notify'] },
  build: {
    vueRouterMode: 'hash',
    // shortcut: Wi-Fi IP is fixed for this local demo, use the deployed HTTPS URL for submission.
    env: { QCLI_API_BASE_URL: 'http://192.168.68.116:5005' },
  },
  devServer: { port: 9000 },
}))
