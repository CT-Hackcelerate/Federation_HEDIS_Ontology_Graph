import { createTheme } from '@mui/material/styles';

/**
 * MUI Theme Configuration for the EHR Care Gap Dashboard.
 * Professional healthcare-inspired color palette.
 */
const theme = createTheme({
  palette: {
    primary: {
      main: '#1a365d',
      light: '#2d4a7c',
      dark: '#0f2744',
    },
    secondary: {
      main: '#3182ce',
    },
    info: {
      main: '#1565c0',
    },
    warning: {
      main: '#f57c00',
    },
    error: {
      main: '#c62828',
    },
    success: {
      main: '#2e7d32',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#1a365d',
      secondary: '#546e7a',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 6,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
  spacing: 8,
});

export default theme;
