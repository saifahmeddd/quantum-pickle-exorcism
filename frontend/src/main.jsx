import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

// index.html contains <div id="root"></div>. createRoot connects React to that
// real DOM element, and render places the App component tree inside it.
createRoot(document.getElementById('root')).render(
  // StrictMode adds development checks that help reveal unsafe React behavior.
  // It does not create a visible element and is removed from production work.
  <StrictMode>
    {/* App is the root of our own component tree. */}
    <App />
  </StrictMode>,
);
