import { createSlice } from '@reduxjs/toolkit';
import {
  ApiError,
  completeTask as completeTaskRequest,
  createTask as createTaskRequest,
  deleteTask as deleteTaskRequest,
  listTasks,
  renameTask as renameTaskRequest,
} from '../../api/client.js';

const initialState = {
  items: [],
  isLoading: false,
  isCreating: false,
  busyTaskId: null,
  error: '',
};

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

const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    tasksLoadingStarted(state) {
      state.isLoading = true;
      state.error = '';
    },
    tasksLoaded(state, action) {
      state.isLoading = false;
      state.items = orderTasks(action.payload);
    },
    taskCreationStarted(state) {
      state.isCreating = true;
      state.error = '';
    },
    taskCreated(state, action) {
      state.isCreating = false;
      state.items = orderTasks([...state.items, action.payload]);
    },
    taskUpdateStarted(state, action) {
      state.busyTaskId = action.payload;
      state.error = '';
    },
    taskUpdated(state, action) {
      state.busyTaskId = null;
      state.items = orderTasks(
        state.items.map(task => task.id === action.payload.id ? action.payload : task),
      );
    },
    taskDeleted(state, action) {
      state.busyTaskId = null;
      state.items = state.items.filter(task => task.id !== action.payload);
    },
    taskRequestFailed(state, action) {
      state.isLoading = false;
      state.isCreating = false;
      state.busyTaskId = null;
      state.error = action.payload;
    },
    tasksCleared() {
      return initialState;
    },
  },
});

export const {
  tasksLoadingStarted,
  tasksLoaded,
  taskCreationStarted,
  taskCreated,
  taskUpdateStarted,
  taskUpdated,
  taskDeleted,
  taskRequestFailed,
  tasksCleared,
} = tasksSlice.actions;

export function loadTasks(signal) {
  return async (dispatch, getState) => {
    dispatch(tasksLoadingStarted());

    try {
      const token = getState().auth.session.id_token;
      const data = await listTasks(token, signal);
      dispatch(tasksLoaded(data.tasks));
    } catch (error) {
      if (error.name !== 'AbortError') {
        dispatch(taskRequestFailed(errorMessage(error)));
      }
    }
  };
}

export function createTask(title) {
  return async (dispatch, getState) => {
    dispatch(taskCreationStarted());

    try {
      const token = getState().auth.session.id_token;
      const task = await createTaskRequest(title, token);
      dispatch(taskCreated(task));
      return true;
    } catch (error) {
      dispatch(taskRequestFailed(errorMessage(error)));
      return false;
    }
  };
}

async function updateOneTask(dispatch, request, id) {
  dispatch(taskUpdateStarted(id));

  try {
    const task = await request();
    dispatch(taskUpdated(task));
    return true;
  } catch (error) {
    dispatch(taskRequestFailed(errorMessage(error)));
    return false;
  }
}

export function completeTask(id) {
  return (dispatch, getState) => updateOneTask(
    dispatch,
    () => completeTaskRequest(id, getState().auth.session.id_token),
    id,
  );
}

export function renameTask(id, title) {
  return (dispatch, getState) => updateOneTask(
    dispatch,
    () => renameTaskRequest(id, title, getState().auth.session.id_token),
    id,
  );
}

export function deleteTask(id) {
  return async (dispatch, getState) => {
    dispatch(taskUpdateStarted(id));

    try {
      await deleteTaskRequest(id, getState().auth.session.id_token);
      dispatch(taskDeleted(id));
      return true;
    } catch (error) {
      dispatch(taskRequestFailed(errorMessage(error)));
      return false;
    }
  };
}

export const selectTasks = state => state.tasks.items;
export const selectIsLoadingTasks = state => state.tasks.isLoading;
export const selectIsCreating = state => state.tasks.isCreating;
export const selectBusyTaskId = state => state.tasks.busyTaskId;
export const selectTaskError = state => state.tasks.error;
export const selectPendingCount = state => (
  state.tasks.items.filter(task => !task.completed_at).length
);

export default tasksSlice.reducer;
