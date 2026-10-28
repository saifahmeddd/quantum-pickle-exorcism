import { createSlice } from '@reduxjs/toolkit';
import { ApiError, login, register } from '../../api/client.js';

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

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    modeChanged(state, action) {
      state.mode = action.payload;
      state.error = '';
    },
    authenticationStarted(state) {
      state.isSubmitting = true;
      state.error = '';
    },
    authenticationSucceeded(state, action) {
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

export const {
  modeChanged,
  authenticationStarted,
  authenticationSucceeded,
  authenticationFailed,
  loggedOut,
} = authSlice.actions;

export function authenticate(credentials) {
  return async (dispatch, getState) => {
    dispatch(authenticationStarted());

    try {
      const mode = getState().auth.mode;
      const request = mode === 'register' ? register : login;
      const session = await request(credentials);

      // Do not retain the unused refresh token in Redux state.
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

export const selectAuthMode = state => state.auth.mode;
export const selectSession = state => state.auth.session;
export const selectIsAuthenticating = state => state.auth.isSubmitting;
export const selectAuthError = state => state.auth.error;

export default authSlice.reducer;
