import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#6a1b9a', // Purple as primary
    },
    secondary: {
      main: '#00897b', // Teal as secondary
    },
    background: {
      default: '#f4f4f9', // Neutral background
      paper: '#ffffff', // For paper and card components
    },
    text: {
      primary: '#333333', // Dark grey for primary text
      secondary: '#666666', // Light grey for secondary text
    },
  },
  typography: {
    fontFamily: 'Rubik, Roboto, Helvetica, Arial, sans-serif', // Apply Rubik globally
    allVariants: {
      color: '#333333', // Set text color globally
    },
  },
});

export default theme;