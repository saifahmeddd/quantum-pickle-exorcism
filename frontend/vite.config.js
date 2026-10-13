import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // This plugin transforms JSX and enables React's fast development refresh.
  plugins: [react()],

  // During development, Vite forwards API calls to the Python server.
  // The browser therefore talks to one origin and does not need CORS setup.
  server: {
    // Use the same IPv4 address shown in the browser run instructions.
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      // React calls relative /auth and /tasks URLs. Vite receives them on 5173
      // and forwards them to the Python API on 8000 during development.
      '/auth': 'http://127.0.0.1:8000',
      '/tasks': 'http://127.0.0.1:8000',
    },
  },
});
