import { useEffect, useState } from 'react';
import {
  ApiError,
  completeTask,
  createTask,
  deleteTask,
  listTasks,
  login,
  register,
  renameTask,
} from './api/client.js';
import AppHeader from './components/AppHeader.jsx';
import AuthForm from './components/AuthForm.jsx';
import TaskForm from './components/TaskForm.jsx';
import TaskList from './components/TaskList.jsx';

// The backend already returns tasks in domain order, but local CRUD updates can
// change that order. This helper copies the array before sorting so React state
// is never mutated directly. Pending tasks come before completed tasks.
function orderTasks(tasks) {
  return [...tasks].sort((left, right) => {
    const completionDifference = Number(Boolean(left.completed_at)) - Number(Boolean(right.completed_at));
    if (completionDifference !== 0) return completionDifference;
    return left.created_at.localeCompare(right.created_at) || left.id.localeCompare(right.id);
  });
}

// Convert technical API errors into short messages that are safe and useful in
// the interface. A 401 receives a clearer authentication-specific explanation.
function errorMessage(error) {
  if (error instanceof ApiError && error.status === 401) {
    return 'Your session is invalid or expired. Log in again.';
  }
  return error.message || 'Something went wrong.';
}

/**
 * App is the root component and the shared application-state owner.
 *
 * It keeps data that several child components need:
 * - the Firebase session returned after registration or login;
 * - the task collection returned by the Python API;
 * - loading, busy, and error states used to explain what the UI is doing.
 * ThemeProvider separately owns the shared visual theme because it is a UI
 * preference rather than authentication data or domain state.
 *
 * App passes data down through props and passes callback functions down for
 * user actions. When a callback receives a successful API response, App updates
 * its state. That state update makes React render the affected UI again.
 *
 * App also chooses the main screen: AuthForm when no session exists, or the
 * task interface after authentication succeeds.
 */
export default function App() {
  // authMode controls which version of AuthForm is displayed.
  const [authMode, setAuthMode] = useState('login');

  // The frontend keeps the Firebase token temporarily so it can send it with
  // protected requests. The stateless backend still verifies every request.
  const [session, setSession] = useState(null);

  // tasks is the shared collection displayed by TaskList and counted by App.
  const [tasks, setTasks] = useState([]);

  // These flags let the UI show progress and prevent duplicate requests.
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState(null);

  // Authentication and task errors are separate because they appear on
  // different screens.
  const [authError, setAuthError] = useState('');
  const [taskError, setTaskError] = useState('');

  // Optional chaining returns undefined while session is null. When login sets
  // a session, idToken changes and triggers the Effect below.
  const idToken = session?.id_token;

  // useEffect runs AFTER React has rendered. In this case it synchronizes the
  // screen with an external system: the Python API.
  useEffect(() => {
    // On the first render there is no session token, so no protected request
    // should be sent. Returning ends this Effect run immediately.
    if (!idToken) return undefined;

    // The controller lets the cleanup function cancel this specific GET
    // request if the user logs out or a different token becomes active.
    const controller = new AbortController();

    // These state updates show the loading UI and remove an older error.
    setIsLoadingTasks(true);
    setTaskError('');

    // listTasks sends GET /tasks with the ID token. Promise callbacks handle
    // the later response without blocking the browser.
    listTasks(idToken, controller.signal)
      // A successful response becomes the task state used by TaskList.
      .then(data => setTasks(orderTasks(data.tasks)))
      .catch(error => {
        // An intentional cancellation is not a user-facing failure.
        if (error.name !== 'AbortError') setTaskError(errorMessage(error));
      })
      .finally(() => {
        // Avoid updating loading state after this Effect has been cleaned up.
        if (!controller.signal.aborted) setIsLoadingTasks(false);
      });

    // React calls this cleanup before rerunning the Effect and when App
    // unmounts. It prevents an outdated response from changing current state.
    return () => controller.abort();

    // Dependency array: run after the first render and whenever idToken changes.
    // Unrelated state updates, such as typing a task title, do not rerun it.
  }, [idToken]);

  // AuthForm calls this handler with its current controlled input values.
  async function handleAuthentication(credentials) {
    // Immediately render the disabled/loading state while awaiting the API.
    setIsAuthenticating(true);
    setAuthError('');

    try {
      // AuthForm supplies credentials; App selects the correct API operation.
      const authenticate = authMode === 'register' ? register : login;
      const newSession = await authenticate(credentials);

      // Setting the session causes a re-render. idToken then becomes available,
      // which starts the task-loading Effect.
      setSession(newSession);
      setTasks([]);
    } catch (error) {
      // A failed request changes only the visible error state.
      setAuthError(errorMessage(error));
    } finally {
      // finally runs after either success or failure.
      setIsAuthenticating(false);
    }
  }

  // Switching form mode is ordinary state-driven conditional rendering.
  function handleModeChange(mode) {
    setAuthMode(mode);
    setAuthError('');
  }

  // Clearing session removes the protected screen on the next render. It also
  // changes idToken to undefined, so the Effect cleans up its request.
  function handleLogout() {
    setSession(null);
    setTasks([]);
    setTaskError('');
  }

  // TaskForm calls this after validating and trimming its local title state.
  async function handleCreate(title) {
    setIsCreating(true);
    setTaskError('');
    try {
      // Store the task returned by the backend because it contains the real ID,
      // timestamps, and normalized title created by the inner application layers.
      const task = await createTask(title, idToken);

      // The updater receives the latest state. Spreading creates a new array;
      // it does not push into and mutate the existing React state array.
      setTasks(current => orderTasks([...current, task]));
      return true;
    } catch (error) {
      setTaskError(errorMessage(error));
      return false;
    } finally {
      setIsCreating(false);
    }
  }

  // Rename and complete both return one updated task. This shared helper avoids
  // repeating their busy, error, and immutable replacement logic.
  async function updateOneTask(id, operation) {
    setBusyTaskId(id);
    setTaskError('');
    try {
      // Complete and rename share the same state update: replace only the task
      // whose ID matches the updated task returned by the backend.
      const updatedTask = await operation();
      setTasks(current => orderTasks(
        current.map(task => task.id === id ? updatedTask : task),
      ));
      return true;
    } catch (error) {
      setTaskError(errorMessage(error));
      return false;
    } finally {
      setBusyTaskId(null);
    }
  }

  // Passing a function delays the API call until updateOneTask executes it.
  function handleComplete(id) {
    return updateOneTask(id, () => completeTask(id, idToken));
  }

  function handleRename(id, title) {
    return updateOneTask(id, () => renameTask(id, title, idToken));
  }

  // Delete differs from update because the successful response removes an
  // object instead of returning a replacement task.
  async function handleDelete(id) {
    setBusyTaskId(id);
    setTaskError('');
    try {
      await deleteTask(id, idToken);

      // filter returns a new array containing every task except the deleted ID.
      setTasks(current => current.filter(task => task.id !== id));
      return true;
    } catch (error) {
      setTaskError(errorMessage(error));
      return false;
    } finally {
      setBusyTaskId(null);
    }
  }

  if (!session) {
    // Conditional rendering keeps protected task components off the screen
    // until authentication has produced a session.
    return (
      <main className="auth-layout">
        <AuthForm
          mode={authMode}
          isSubmitting={isAuthenticating}
          error={authError}
          onSubmit={handleAuthentication}
          onModeChange={handleModeChange}
        />
      </main>
    );
  }

  // This value is derived from tasks, so it does not need separate state.
  const pendingCount = tasks.filter(task => !task.completed_at).length;

  return (
    <main className="app-shell">
      {/* AppHeader receives session data normally but reads theme from context. */}
      <AppHeader
        email={session.email}
        pendingCount={pendingCount}
        onLogout={handleLogout}
      />

      <section className="task-panel" aria-labelledby="task-panel-title">
        <h2 id="task-panel-title" className="sr-only">Task manager</h2>

        {/* Props send data and callbacks from App down to TaskForm. */}
        <TaskForm isSubmitting={isCreating} onCreate={handleCreate} />

        {/* && renders the paragraph only when taskError is a non-empty string. */}
        {taskError && <p className="message error" role="alert">{taskError}</p>}

        {/* The ternary renders exactly one branch: loading text or the list. */}
        {isLoadingTasks ? (
          <p className="loading">Loading tasks…</p>
        ) : (
          /* TaskList reads the array and callbacks; App remains their owner. */
          <TaskList
            tasks={tasks}
            busyTaskId={busyTaskId}
            onComplete={handleComplete}
            onRename={handleRename}
            onDelete={handleDelete}
          />
        )}
      </section>
    </main>
  );
}
