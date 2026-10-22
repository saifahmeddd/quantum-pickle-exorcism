import { createContext, useContext, useEffect, useState } from 'react';

// ThemeContext is a shared channel for a simple UI preference. null represents
// a missing provider, while the real context value is always an object.
const ThemeContext = createContext(null);

/**
 * ThemeProvider owns the light/dark preference for every component below it.
 * Its Effect synchronizes React's theme state with the root HTML element so the
 * CSS theme applies to the whole page, not just one component.
 */
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;

    return () => {
      delete document.documentElement.dataset.theme;
    };
  }, [theme]);

  function toggleTheme() {
    setTheme(current => current === 'light' ? 'dark' : 'light');
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Components call this custom Hook instead of importing the context directly.
 * The guard makes incorrect use outside ThemeProvider easy to understand.
 */
export function useTheme() {
  const context = useContext(ThemeContext);

  if (context === null) {
    throw new Error('useTheme must be used inside ThemeProvider.');
  }

  return context;
}
