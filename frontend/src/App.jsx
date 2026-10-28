import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  ApiError,
  completeTask as completeTaskRequest,
  deleteTask as deleteTaskRequest,
  listTasks,
  renameTask as renameTaskRequest,
} from './api/client.js';
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
  createTask,
  selectIsCreating,
  selectTaskCreationError,
  taskCreationReset,
} from './features/tasks/taskCreationSlice.js';
import AppHeader from './components/AppHeader.jsx';
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

export default function App() {
  const dispatch = useDispatch();

  // Redux owns authentication and task creation.
  const authMode = useSelector(selectAuthMode);
  const session = useSelector(selectSession);
  const isAuthenticating = useSelector(selectIsAuthenticating);
  const authError = useSelector(selectAuthError);
  const isCreating = useSelector(selectIsCreating);
  const creationError = useSelector(selectTaskCreationError);

  // The task list and remaining requests use local React state.
  const [tasks, setTasks] = useState([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState(null);
  const [taskError, setTaskError] = useState('');

  const idToken = session?.id_token;

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

  function handleAuthentication(credentials) {
    return dispatch(authenticate(credentials));
  }

  function handleModeChange(mode) {
    dispatch(modeChanged(mode));
  }

  function handleLogout() {
    dispatch(loggedOut());
    dispatch(taskCreationReset());
    setTasks([]);
    setTaskError('');
  }

  async function handleCreate(title) {
    const task = await dispatch(createTask(title));
    if (task === null) return false;

    setTasks(current => orderTasks([...current, task]));
    return true;
  }

  async function updateOneTask(id, request) {
    setBusyTaskId(id);
    setTaskError('');

    try {
      const updatedTask = await request();
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
    return updateOneTask(id, () => completeTaskRequest(id, idToken));
  }

  function handleRename(id, title) {
    return updateOneTask(id, () => renameTaskRequest(id, title, idToken));
  }

  async function handleDelete(id) {
    setBusyTaskId(id);
    setTaskError('');

    try {
      await deleteTaskRequest(id, idToken);
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

  const pendingCount = tasks.filter(task => !task.completed_at).length;

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

        {creationError && <p className="message error" role="alert">{creationError}</p>}
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
