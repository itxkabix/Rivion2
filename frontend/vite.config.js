import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        host: '0.0.0.0',
        strictPort: false,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                rewrite: (path) => path,
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true,
        minify: 'terser',
    },
    define: {
        'process.env': {},
    },
})
