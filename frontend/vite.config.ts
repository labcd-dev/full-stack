import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Long-running design jobs use SSE; default proxy timeout is ~2 minutes.
        timeout: 0,
        proxyTimeout: 0,
      },
    },
  },
})
