import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice.js';
import taskCreationReducer from '../features/tasks/taskCreationSlice.js';

// configureStore combines the slices and includes thunk middleware.
export const store = configureStore({
  reducer: {
    auth: authReducer,
    taskCreation: taskCreationReducer,
  },
});
