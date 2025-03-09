import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Phonebook from './components/PhoneBook/Phonebook';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();


const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Phonebook />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
