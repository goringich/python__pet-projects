import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import darkTheme from './theme';
import Phonebook from './components/PhoneBook/Phonebook';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();


const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <Router>  
          <Routes>
            <Route path="/" element={<Phonebook />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </ThemeProvider>
  );
};

export default App;
