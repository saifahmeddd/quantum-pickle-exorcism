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
import AuthForm from './components/AuthForm.jsx';
import TaskForm from './components/TaskForm.jsx';
import TaskList from './components/TaskList.jsx';

function orderTasks(tasks) {
  return [...tasks].sort((left, right) => {
    const completionDifference = Number(Boolean(left.completed_at)) - Number(Boolean(right.completed_at));
    if (completionDifference !== 0) return completionDifference;
    return left.created_at.localeCompare(right.created_at) || left.id.localeCompare(right.id);
  });
}

function errorMessage(error) {
  if (error instanceof ApiError && error.status === 401) {
    return 'Your session is invalid or expired. Log in again.';
  }
  return error.message || 'Something went wrong.';
}

/**
 * App is the root component and the shared-state owner.
 *
 * It keeps data that several child components need:
 * - the Firebase session returned after registration or login;
 * - the task collection returned by the Python API;
 * - loading, busy, and error states used to explain what the UI is doing.
 *
 * App passes data down through props and passes callback functions down for
 * user actions. When a callback receives a successful API response, App updates
 * its state. That state update makes React render the affected UI again.
 *
 * App also chooses the main screen: AuthForm when no session exists, or the
 * task interface after authentication succeeds.
 */
export default function App() {
  const [authMode, setAuthMode] = useState('login');
  const [session, setSession] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState(null);
  const [authError, setAuthError] = useState('');
  const [taskError, setTaskError] = useState('');

  const idToken = session?.id_token;

  // This Effect loads the signed-in user's tasks when idToken changes from
  // undefined to a verified session token. The cleanup aborts an old request
  // if the component is removed or another token replaces the current one.
  useEffect(() => {
    if (!idToken) return undefined;

    const controller = new AbortController();
    setIsLoadingTasks(true);
    setTaskError('');

    listTasks(idToken, controller.signal)
      .then(data => setTasks(orderTasks(data.tasks)))
      .catch(error => {
        if (error.name !== 'AbortError') setTaskError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoadingTasks(false);
      });

    return () => controller.abort();
  }, [idToken]);

  async function handleAuthentication(credentials) {
    setIsAuthenticating(true);
    setAuthError('');

    try {
      // AuthForm supplies credentials; App selects the correct API operation.
      const authenticate = authMode === 'register' ? register : login;
      const newSession = await authenticate(credentials);
      setSession(newSession);
      setTasks([]);
    } catch (error) {
      setAuthError(errorMessage(error));
    } finally {
      setIsAuthenticating(false);
    }
  }

  function handleModeChange(mode) {
    setAuthMode(mode);
    setAuthError('');
  }

  function handleLogout() {
    setSession(null);
    setTasks([]);
    setTaskError('');
  }

  async function handleCreate(title) {
    setIsCreating(true);
    setTaskError('');
    try {
      // Store the task returned by the backend because it contains the real ID,
      // timestamps, and normalized title created by the inner application layers.
      const task = await createTask(title, idToken);
      setTasks(current => orderTasks([...current, task]));
      return true;
    } catch (error) {
      setTaskError(errorMessage(error));
      return false;
    } finally {
      setIsCreating(false);
    }
  }

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

  function handleComplete(id) {
    return updateOneTask(id, () => completeTask(id, idToken));
  }

  function handleRename(id, title) {
    return updateOneTask(id, () => renameTask(id, title, idToken));
  }

  async function handleDelete(id) {
    setBusyTaskId(id);
    setTaskError('');
    try {
      await deleteTask(id, idToken);
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
      <header className="app-header">
        <div>
          <div className="eyebrow">DDD + React</div>
          <h1>My tasks</h1>
          <p className="muted">
            Signed in as {session.email} · {pendingCount} pending
          </p>
        </div>
        <button className="secondary" onClick={handleLogout}>Log out</button>
      </header>

      <section className="task-panel" aria-labelledby="task-panel-title">
        <h2 id="task-panel-title" className="sr-only">Task manager</h2>
        <TaskForm isSubmitting={isCreating} onCreate={handleCreate} />

        {taskError && <p className="message error" role="alert">{taskError}</p>}

        {isLoadingTasks ? (
          <p className="loading">Loading tasks…</p>
        ) : (
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
