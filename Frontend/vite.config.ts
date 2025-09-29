import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },

  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:3001',
        changeOrigin: true,
      },
    },
    // ✨ 파일 변경 감지를 위해 Polling 방식을 사용하도록 설정합니다.
    // watch: {
    //   usePolling: true,
    //  },
 // },
})
