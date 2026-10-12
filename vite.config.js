import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/', // GitHub Pages project site path
  build: {
    modulePreload: {
      resolveDependencies(filename, deps) {
        return deps.filter(dep => !dep.includes('vendor-charts') && !dep.includes('vendor-export'))
      }
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/recharts')) {
            return 'vendor-charts'
          }
          if (id.includes('node_modules/jspdf') || id.includes('node_modules/jspdf-autotable') || id.includes('node_modules/xlsx')) {
            return 'vendor-export'
          }
          if (id.includes('node_modules/@supabase')) {
            return 'vendor-supabase'
          }
        }
      }
    }
  }
})
