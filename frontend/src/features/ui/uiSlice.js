import { createSlice } from '@reduxjs/toolkit';

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    theme: 'light',
  },
  reducers: {
    themeToggled(state) {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
  },
});

export const { themeToggled } = uiSlice.actions;
export const selectTheme = state => state.ui.theme;

export default uiSlice.reducer;
