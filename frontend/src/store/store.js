import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice.js';
import tasksReducer from '../features/tasks/tasksSlice.js';

/**
 * The store is the single container for shared Redux state.
 * Each key below owns one branch of that state and delegates updates to its
 * slice reducer.
 *
 * configureStore also adds Redux thunk middleware. Middleware runs between
 * dispatch and the reducers. Thunk middleware lets us dispatch an async
 * function for API work; that function later dispatches ordinary actions that
 * the reducers understand.
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: tasksReducer,
  },
});
