import { createSlice } from '@reduxjs/toolkit';
import { ApiError, createTask as createTaskRequest } from '../../api/client.js';

// Redux owns only the state needed by the create-task request.
const initialState = {
  isCreating: false,
  error: '',
};

function errorMessage(error) {
  if (error instanceof ApiError && error.status === 401) {
    return 'Your session is invalid or expired. Log in again.';
  }

  return error.message || 'Something went wrong.';
}

/**
 * This slice demonstrates Redux state, reducer functions, and generated action
 * creators without moving the entire task screen into Redux.
 */
const taskCreationSlice = createSlice({
  name: 'taskCreation',
  initialState,
  reducers: {
    taskCreationStarted(state) {
      state.isCreating = true;
      state.error = '';
    },
    taskCreationSucceeded(state) {
      state.isCreating = false;
    },
    taskCreationFailed(state, action) {
      state.isCreating = false;
      state.error = action.payload;
    },
    taskCreationReset() {
      return initialState;
    },
  },
});

// createSlice generates these action creators from the reducer names above.
export const {
  taskCreationStarted,
  taskCreationSucceeded,
  taskCreationFailed,
  taskCreationReset,
} = taskCreationSlice.actions;

/**
 * Dispatch can send this function because configureStore includes thunk
 * middleware. The thunk reads the auth token, calls the API, and dispatches
 * normal actions that the reducers understand.
 */
export function createTask(title) {
  return async (dispatch, getState) => {
    dispatch(taskCreationStarted());

    try {
      const token = getState().auth.session.id_token;
      const task = await createTaskRequest(title, token);
      dispatch(taskCreationSucceeded());

      // App keeps the task list in local React state, so return the new task.
      return task;
    } catch (error) {
      dispatch(taskCreationFailed(errorMessage(error)));
      return null;
    }
  };
}

// Selectors hide the store's shape from components.
export const selectIsCreating = state => state.taskCreation.isCreating;
export const selectTaskCreationError = state => state.taskCreation.error;

export default taskCreationSlice.reducer;
