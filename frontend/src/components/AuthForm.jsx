import { useState } from 'react';

/**
 * AuthForm displays both registration and login using one reusable form.
 *
 * Props received from App:
 * - mode decides which labels and submit action the user sees;
 * - isSubmitting disables repeated submissions while the request is running;
 * - error displays a safe error returned by App;
 * - onSubmit sends the entered credentials upward;
 * - onModeChange asks App to switch between login and registration.
 *
 * Email and password are local state because only this form needs the values
 * while the user is typing. This component never calls Firebase or fetch
 * directly; App receives the values and delegates the request to the API client.
 */
export default function AuthForm({ mode, isSubmitting, error, onSubmit, onModeChange }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // This is a derived value calculated from props, so it does not need state.
  const isRegistering = mode === 'register';

  async function handleSubmit(event) {
    // Prevent the browser's default form navigation so React stays in control.
    event.preventDefault();

    // Props move the user action upward. App performs the API request because
    // App owns the session that will be created by a successful response.
    await onSubmit({ email: email.trim(), password });
  }

  return (
    <section className="auth-card" aria-labelledby="auth-title">
      <div className="eyebrow">React + Onion Architecture</div>
      <h1 id="auth-title">{isRegistering ? 'Create an account' : 'Welcome back'}</h1>
      <p className="muted">
        {isRegistering
          ? 'Register with Firebase, then manage your own tasks.'
          : 'Log in to load the tasks owned by your account.'}
      </p>

      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Email
          {/* value + onChange make this a controlled React input. */}
          <input
            type="email"
            value={email}
            onChange={event => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </label>

        <label>
          Password
          {/* Each keystroke updates local state and triggers a small re-render. */}
          <input
            type="password"
            value={password}
            onChange={event => setPassword(event.target.value)}
            autoComplete={isRegistering ? 'new-password' : 'current-password'}
            minLength={6}
            required
          />
        </label>

        {/* Render the error element only when App supplies an error message. */}
        {error && <p className="message error" role="alert">{error}</p>}

        <button className="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Please wait…' : isRegistering ? 'Register' : 'Log in'}
        </button>
      </form>

      <button
        className="text-button"
        type="button"
        onClick={() => onModeChange(isRegistering ? 'login' : 'register')}
      >
        {isRegistering
          ? 'Already registered? Log in'
          : 'Need an account? Register'}
      </button>
    </section>
  );
}
