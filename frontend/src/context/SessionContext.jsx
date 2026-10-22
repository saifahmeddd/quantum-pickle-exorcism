import { createContext, useContext, useState } from 'react';

// Context creates one shared channel for session data. The initial null here
// means "no provider was found"; the session value inside the provider may also
// be null before the user logs in, so the provider exposes an object around it.
const SessionContext = createContext(null);

/**
 * SessionProvider owns the authenticated session for the component tree below.
 * Any descendant can read or update that session through useSession without
 * receiving it through every intermediate component as a prop.
 */
export function SessionProvider({ children }) {
  const [session, setSession] = useState(null);

  return (
    <SessionContext.Provider value={{ session, setSession }}>
      {children}
    </SessionContext.Provider>
  );
}

/**
 * This custom Hook gives components a simple, named way to consume the context.
 * The guard produces a clear error if it is ever used outside SessionProvider.
 */
export function useSession() {
  const context = useContext(SessionContext);

  if (context === null) {
    throw new Error('useSession must be used inside SessionProvider.');
  }

  return context;
}
