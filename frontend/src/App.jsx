import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  authenticate,
  loggedOut,
  modeChanged,
  selectAuthError,
  selectAuthMode,
  selectIsAuthenticating,
  selectSession,
} from './features/auth/authSlice.js';
import {
  completeTask,
  createTask,
  deleteTask,
  loadTasks,
  renameTask,
  selectBusyTaskId,
  selectIsCreating,
  selectIsLoadingTasks,
  selectPendingCount,
  selectTaskError,
  selectTasks,
  tasksCleared,
} from './features/tasks/tasksSlice.js';
import AppHeader from './components/AppHeader.jsx';
import AuthForm from './components/AuthForm.jsx';
import TaskForm from './components/TaskForm.jsx';
import TaskList from './components/TaskList.jsx';

/**
 * App reads shared Redux state and dispatches user actions. Forms still keep
 * unfinished input locally because no other component needs that temporary
 * data. ThemeProvider separately owns the visual theme through Context.
 */
export default function App() {
  // useDispatch gives components the store's dispatch function. Dispatch sends
  // actions or thunks into the Redux flow.
  const dispatch = useDispatch();

  // useSelector runs selectors against current store state and re-renders App
  // when one of these selected values changes.
  const authMode = useSelector(selectAuthMode);
  const session = useSelector(selectSession);
  const isAuthenticating = useSelector(selectIsAuthenticating);
  const authError = useSelector(selectAuthError);
  const tasks = useSelector(selectTasks);
  const isLoadingTasks = useSelector(selectIsLoadingTasks);
  const isCreating = useSelector(selectIsCreating);
  const busyTaskId = useSelector(selectBusyTaskId);
  const taskError = useSelector(selectTaskError);
  const pendingCount = useSelector(selectPendingCount);

  const idToken = session?.id_token;

  // Load the authenticated user's tasks whenever the ID token changes.
  useEffect(() => {
    if (!idToken) return undefined;

    const controller = new AbortController();
    dispatch(loadTasks(controller.signal));

    // Cancel an outdated request when the token changes or App unmounts.
    return () => controller.abort();
  }, [dispatch, idToken]);

  function handleAuthentication(credentials) {
    // authenticate is a thunk. Middleware runs it, then it dispatches the
    // started/succeeded/failed actions handled by the auth slice reducers.
    return dispatch(authenticate(credentials));
  }

  function handleModeChange(mode) {
    // modeChanged(mode) creates an action; dispatch sends it to the reducer.
    dispatch(modeChanged(mode));
  }

  function handleLogout() {
    dispatch(loggedOut());
    dispatch(tasksCleared());
  }

  function handleCreate(title) {
    return dispatch(createTask(title));
  }

  function handleComplete(id) {
    return dispatch(completeTask(id));
  }

  function handleRename(id, title) {
    return dispatch(renameTask(id, title));
  }

  function handleDelete(id) {
    return dispatch(deleteTask(id));
  }

  if (!session) {
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

  return (
    <main className="app-shell">
      <AppHeader
        email={session.email}
        pendingCount={pendingCount}
        onLogout={handleLogout}
      />

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
