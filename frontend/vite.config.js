import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  // During development, Vite forwards API calls to the Python server.
  // The browser therefore talks to one origin and does not need CORS setup.
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/tasks': 'http://127.0.0.1:8000',
    },
  },
});
