import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import { ThemeProvider } from '@mui/material/styles';
import theme from './theme'; // your custom MUI theme

import { AuthProvider } from './components/auth/AuthContext'; // adjust the path

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    <AuthProvider>
      <App />
    </AuthProvider>
  </ThemeProvider>
);

reportWebVitals();
