import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice.js';
import tasksReducer from '../features/tasks/tasksSlice.js';
import uiReducer from '../features/ui/uiSlice.js';

// configureStore combines the slices and includes thunk middleware.
export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: tasksReducer,
    ui: uiReducer,
  },
});
