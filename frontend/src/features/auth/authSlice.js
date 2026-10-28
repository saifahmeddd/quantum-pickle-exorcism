import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
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

export const authenticate = createAsyncThunk(
  'auth/authenticate',
  async (credentials, { getState, rejectWithValue }) => {
    try {
      const mode = getState().auth.mode;
      const request = mode === 'register' ? register : login;
      const session = await request(credentials);

      return {
        email: session.email,
        id_token: session.id_token,
      };
    } catch (error) {
      return rejectWithValue(errorMessage(error));
    }
  },
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    modeChanged(state, action) {
      state.mode = action.payload;
      state.error = '';
    },
    loggedOut(state) {
      state.session = null;
      state.error = '';
    },
  },
  extraReducers: builder => {
    builder
      .addCase(authenticate.pending, state => {
        state.isSubmitting = true;
        state.error = '';
      })
      .addCase(authenticate.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.session = action.payload;
      })
      .addCase(authenticate.rejected, (state, action) => {
        state.isSubmitting = false;
        state.error = action.payload || action.error.message;
      });
  },
});

export const {
  modeChanged,
  loggedOut,
} = authSlice.actions;

export const selectAuthMode = state => state.auth.mode;
export const selectSession = state => state.auth.session;
export const selectIsAuthenticating = state => state.auth.isSubmitting;
export const selectAuthError = state => state.auth.error;

export default authSlice.reducer;
