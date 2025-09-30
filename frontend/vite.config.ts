import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
      theme: {
        options: {
          customProperties: true,
        },
        themes: {
          light: {
            dark: false,
            colors: {
              primary: '#304E69',
              secondary: '#C79657',
              accent: '#C79657',
              background: '#DDEAF4',
              surface: '#FFFFFF',
              'primary-darken-1': '#1F3A52',
              'secondary-darken-1': '#A67A43',
            },
          },
          dark: {
            dark: true,
            colors: {
              primary: '#5B7185',
              secondary: '#C79657',
              accent: '#C79657',
              background: '#304E69',
              surface: '#5B7185',
              'primary-darken-1': '#304E69',
              'secondary-darken-1': '#A67A43',
            },
          },
        },
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['.ngrok-free.app', '.ngrok-free.dev', '.ngrok.io'],
    cors: {
      origin: ['http://localhost:8000', 'https://semiurban-quakingly-moises.ngrok-free.dev'],
      credentials: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['vuetify'],
          utils: ['axios', 'date-fns', 'qrcode'],
        },
      },
    },
  },
})