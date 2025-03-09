
import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#9c27b0', 
    },
    background: {
      default: '#121212', 
      paper: '#1E1E1E',   
    },
    text: {
      primary: '#FFFFFF', 
      secondary: '#B0B0B0',
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
});

export default darkTheme;
