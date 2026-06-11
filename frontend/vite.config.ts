import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/query': {
        target: 'http://127.0.0.1:8000',
        configure: (proxy) => {
          // Tell the upstream server not to compress responses.
          // Without this, http-proxy buffers the entire response to decompress
          // it before forwarding — which breaks SSE streaming.
          proxy.on('proxyReq', (proxyReq) => {
            proxyReq.setHeader('Accept-Encoding', 'identity')
          })
        },
      },
      '/ingest': 'http://127.0.0.1:8000',
    },
  },
})
