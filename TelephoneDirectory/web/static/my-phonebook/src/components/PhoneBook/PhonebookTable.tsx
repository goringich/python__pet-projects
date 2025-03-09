import React from 'react';
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
  Paper,
} from '@mui/material';
import { RecordData, ModalType, FormFields } from './types';

interface PhonebookTableProps {
  data: RecordData[];
  searchResults: RecordData[] | null;
  openModal: (type: ModalType, prefill?: Partial<FormFields>) => void;
  deleteRecord: (record: RecordData) => void;
}

const PhonebookTable: React.FC<PhonebookTableProps> = ({
  data,
  searchResults,
  openModal,
  deleteRecord,
}) => {
  const records = searchResults || data;
  return (
    <Paper sx={{ mt: 2 }}>
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
            <TableRow key={index}>
              <TableCell>{record.Name}</TableCell>
              <TableCell>{record.Surname}</TableCell>
              <TableCell>{record.Phone}</TableCell>
              <TableCell>{record.BirthDate || 'N/A'}</TableCell>
              <TableCell>
                <Button
                  size="small"
                  onClick={() =>
                    openModal('update', {
                      Name: record.Name,
                      Surname: record.Surname,
                    })
                  }
                >
                  Edit
                </Button>
                <Button
                  size="small"
                  color="error"
                  onClick={() => {
                    if (
                      window.confirm(
                        `Are you sure you want to delete ${record.Name} ${record.Surname}?`
                      )
                    ) {
                      deleteRecord(record);
                    }
                  }}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Paper>
  );
};

export default PhonebookTable;
