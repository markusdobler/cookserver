import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd()+"/..", '')
  const basePath = env.VITE_BASE_PATH || '/'
  const backendPort = env.PORT || '7395'
  const apiTarget = env.VITE_API_URL || `http://localhost:${backendPort}`

  return {
    plugins: [vue()],
    base: basePath,
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        }
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      }
    }
  }
})
