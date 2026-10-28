import { useTheme } from '../context/ThemeContext.jsx';

export default function AppHeader({ email, pendingCount, onLogout }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="app-header">
      <div>
        <div className="eyebrow">DDD + React</div>
        <h1>My tasks</h1>
        <p className="muted">
          Signed in as {email} · {pendingCount} pending
        </p>
      </div>
      <div className="header-actions">
        <button className="secondary" onClick={toggleTheme}>
          {theme === 'light' ? 'Dark mode' : 'Light mode'}
        </button>
        <button className="secondary" onClick={onLogout}>Log out</button>
      </div>
    </header>
  );
}
