import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// React "islands" for the Django site: `npm run build` writes static/frontend/islands.{js,css},
// which templates load and mount into elements marked data-react-island="<Name>".
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(import.meta.dirname, './src') } },
  base: '/static/frontend/',
  build: {
    outDir: path.resolve(import.meta.dirname, '../static/frontend'),
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      input: path.resolve(import.meta.dirname, 'src/islands.tsx'),
      output: {
        // Fixed names: Django cache-busts with ?v=<mtime> (see chatbot/context_processors.py).
        entryFileNames: 'islands.js',
        // React gets its own content-hashed chunk. The entry is loaded as islands.js?v=…, so if
        // lazy chunks imported React from the entry ("../islands.js", no ?v) the browser would
        // run a second copy of React and hooks would crash. A hashed chunk has one URL for all.
        codeSplitting: {
          groups: [{ name: 'runtime', test: /runtime|preload-helper/ }, { name: 'react', test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/ }],
        },
        chunkFileNames: 'chunks/[name]-[hash].js', // hashed: imported by islands.js without ?v=
        assetFileNames: (info) => (info.names?.[0]?.endsWith('.css') ? 'islands.css' : 'assets/[name][extname]'),
      },
    },
  },
})
