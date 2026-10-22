import { useSession } from '../context/SessionContext.jsx';

/**
 * AppHeader reads the authenticated session directly from context. App only
 * passes header-specific values and behavior, so the session does not need to
 * travel through props.
 */
export default function AppHeader({ pendingCount, onLogout }) {
  const { session } = useSession();

  return (
    <header className="app-header">
      <div>
        <div className="eyebrow">DDD + React</div>
        <h1>My tasks</h1>
        <p className="muted">
          Signed in as {session.email} · {pendingCount} pending
        </p>
      </div>
      <button className="secondary" onClick={onLogout}>Log out</button>
    </header>
  );
}
