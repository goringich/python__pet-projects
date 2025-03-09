import React from 'react';
import { Alert } from '@mui/material';

interface MessageDisplayProps {
  type: 'error' | 'success';
  message: string;
}

const MessageDisplay: React.FC<MessageDisplayProps> = ({ type, message }) => {
  return (
    <Alert 
      severity={type} 
      sx={{ mb: 2 }}
    >
      {message}
    </Alert>
  );
};

export default MessageDisplay;