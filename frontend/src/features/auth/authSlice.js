import { createSlice } from '@reduxjs/toolkit';
import { ApiError, login, register } from '../../api/client.js';

// State is the shared data Redux remembers for authentication.
const initialState = {
  mode: 'login',
  session: null,
  isSubmitting: false,
  error: '',
};

function errorMessage(error) {
  if (error instanceof ApiError && error.status === 401) {
    return 'Your session is invalid or expired. Log in again.';
  }

  return error.message || 'Something went wrong.';
}

/**
 * A slice groups one feature's state, reducer functions, and action creators.
 * Reducers describe synchronous state changes. Redux Toolkit uses Immer, so
 * this readable mutation-style code safely creates immutable state updates.
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    modeChanged(state, action) {
      // The action payload carries the new mode into the reducer.
      state.mode = action.payload;
      state.error = '';
    },
    authenticationStarted(state) {
      state.isSubmitting = true;
      state.error = '';
    },
    authenticationSucceeded(state, action) {
      // The session holds the email and ID token returned after authentication.
      state.isSubmitting = false;
      state.session = action.payload;
    },
    authenticationFailed(state, action) {
      state.isSubmitting = false;
      state.error = action.payload;
    },
    loggedOut(state) {
      state.session = null;
      state.error = '';
    },
  },
});

// createSlice generates action creators for every reducer function.
export const {
  modeChanged,
  authenticationStarted,
  authenticationSucceeded,
  authenticationFailed,
  loggedOut,
} = authSlice.actions;

/**
 * This thunk contains the asynchronous authentication flow. Thunk middleware
 * receives the function, gives it dispatch/getState, and keeps credentials out
 * of normal Redux actions and action history.
 */
export function authenticate(credentials) {
  return async (dispatch, getState) => {
    dispatch(authenticationStarted());

    try {
      const mode = getState().auth.mode;
      const request = mode === 'register' ? register : login;
      const session = await request(credentials);

      // Redux only needs these fields. The refresh token is intentionally not
      // copied into the store because this app does not implement token refresh.
      dispatch(authenticationSucceeded({
        email: session.email,
        id_token: session.id_token,
      }));
      return true;
    } catch (error) {
      dispatch(authenticationFailed(errorMessage(error)));
      return false;
    }
  };
}

// Selectors are small functions that read one value from the store.
export const selectAuthMode = state => state.auth.mode;
export const selectSession = state => state.auth.session;
export const selectIsAuthenticating = state => state.auth.isSubmitting;
export const selectAuthError = state => state.auth.error;

// The store needs the slice's reducer to handle auth actions.
export default authSlice.reducer;
