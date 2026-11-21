import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: { outDir: '../src/signature_chat/web', emptyOutDir: true },
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8780', changeOrigin: true },
      '/images': { target: 'http://127.0.0.1:8780', changeOrigin: true },
    },
  },
})
