import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vue core - always needed
          'vue-vendor': ['vue', 'vue-router'],
        },
      },
    },
  },
  server: {
    proxy: {
      // WebSocket proxies must come first (more specific paths)
      '/api/assistant/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/api/spec-creation/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      // HTTP API proxy
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
