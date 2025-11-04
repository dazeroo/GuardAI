import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // 기존 import 유지

export default defineConfig({
  plugins: [react()],

  // 1. 기존의 경로 별칭(alias) 설정은 그대로 유지합니다.
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },

  // 2. 새로운 프록시(proxy) 설정을 여기에 추가합니다.
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/routers': {
        target: 'http://127.0.0.1:8000',   //http://0.0.0.0:8000
        changeOrigin: true,
      },
    },
    // 파일 변경 감지를 위해 Polling 방식을 사용하도록 설정합니다.
    // watch: {
    //   usePolling: true,
    //  },
  },
})
