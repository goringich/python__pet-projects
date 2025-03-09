import React from 'react';
import { 
  Table, TableBody, TableCell, TableContainer, TableHead, 
  TableRow, Paper, Button, Box, Typography 
} from '@mui/material';
import { Record } from '../types';
import { api, parseErrorMessage } from '../api';

interface RecordsTableProps {
  records: Record[];
  onRecordDelete: (name: string, surname: string) => void;
  onRecordEdit: (name: string, surname: string) => void;
  onRefreshNeeded: () => void;
  setMessage: (type: 'error' | 'success', text: string) => void;
}

const RecordsTable: React.FC<RecordsTableProps> = ({ 
  records, 
  onRecordDelete, 
  onRecordEdit, 
  onRefreshNeeded,
  setMessage
}) => {
  const handleDelete = async (name: string, surname: string) => {
    if (window.confirm(`Are you sure you want to delete ${name} ${surname}?`)) {
      try {
        await api.deleteRecord({ Name: name, Surname: surname });
        setMessage('success', 'Record deleted successfully.');
        onRecordDelete(name, surname);
        onRefreshNeeded();
      } catch (error) {
        const errorMsg = parseErrorMessage(error) || 'Error deleting record.';
        setMessage('error', errorMsg);
      }
    }
  };

  if (!records || records.length === 0) {
    return (
      <Box my={2} textAlign="center">
        <Typography variant="body1">No records found.</Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ mb: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Surname</TableCell>
            <TableCell>Phone</TableCell>
            <TableCell>Birth Date</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {records.map((record, index) => (
            <TableRow key={`${record.Name}-${record.Surname}-${index}`}>
              <TableCell>{record.Name}</TableCell>
              <TableCell>{record.Surname}</TableCell>
              <TableCell>{record.Phone}</TableCell>
              <TableCell>{record.BirthDate || 'N/A'}</TableCell>
              <TableCell>
                <Button 
                  variant="outlined" 
                  size="small" 
                  sx={{ mr: 1 }}
                  onClick={() => onRecordEdit(record.Name, record.Surname)}
                >
                  Edit
                </Button>
                <Button 
                  variant="outlined" 
                  color="error" 
                  size="small"
                  onClick={() => handleDelete(record.Name, record.Surname)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default RecordsTable;