import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import App from './App.jsx';
import { ThemeProvider } from './context/ThemeContext.jsx';
import { store } from './store/store.js';
import './styles.css';

// index.html contains <div id="root"></div>. createRoot connects React to that
// real DOM element, and render places the App component tree inside it.
createRoot(document.getElementById('root')).render(
  // StrictMode adds development checks that help reveal unsafe React behavior.
  // It does not create a visible element and is removed from production work.
  <StrictMode>
    {/* Provider makes the Redux store available to every component below it. */}
    <Provider store={store}>
      {/* The provider shares the UI theme with App and every child component. */}
      <ThemeProvider>
        {/* App is the root of our visible component tree. */}
        <App />
      </ThemeProvider>
    </Provider>
  </StrictMode>,
);
