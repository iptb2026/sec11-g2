import { fileURLToPath } from 'node:url'
import { defineConfig } from '#q-app'

export default defineConfig(() => ({
  boot: ['axios'],
  css: ['app.css'],
  extras: ['material-icons'],
  build: {
    extendViteConf (viteConf) {
      viteConf.resolve ??= {}
      viteConf.resolve.alias ??= {}
      viteConf.resolve.alias.src = fileURLToPath(new URL('./src', import.meta.url))
    },
    vueRouterMode: 'hash',
    vueRouterBase: '/costas-wui/',
    publicPath: '/costas-wui/'
  },
  devServer: { port: 9000, open: false },
  framework: { plugins: ['Notify', 'Dialog'] },
  animations: []
}))
