import { createSlice } from '@reduxjs/toolkit';
import { ApiError, createTask as createTaskRequest } from '../../api/client.js';

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

export const {
  taskCreationStarted,
  taskCreationSucceeded,
  taskCreationFailed,
  taskCreationReset,
} = taskCreationSlice.actions;

export function createTask(title) {
  return async (dispatch, getState) => {
    dispatch(taskCreationStarted());

    try {
      const token = getState().auth.session.id_token;
      const task = await createTaskRequest(title, token);
      dispatch(taskCreationSucceeded());

      // App owns the task list, so return the created task to it.
      return task;
    } catch (error) {
      dispatch(taskCreationFailed(errorMessage(error)));
      return null;
    }
  };
}

export const selectIsCreating = state => state.taskCreation.isCreating;
export const selectTaskCreationError = state => state.taskCreation.error;

export default taskCreationSlice.reducer;
