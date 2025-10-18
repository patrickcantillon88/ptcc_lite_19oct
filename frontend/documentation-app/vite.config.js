import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5189,
    open: false,
    cors: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})