import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// Dev: the API runs on :8000 (make backend), Vite proxies /api to it.
// Build: frontend/dist is served by the backend itself, same origin.
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'N.A.P.L.E.S.',
        short_name: 'NAPLES',
        description: 'Agenti AI per la resilienza urbana di Napoli',
        lang: 'it',
        start_url: '/cittadino',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#161616',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: 'icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/docs/],
        globPatterns: ['**/*.{js,css,html,svg,woff2,ico,png}'],
      },
    }),
  ],
  // host: true also listens on the local network, so a phone on the same Wi-Fi can open it
  server: {
    host: true,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
