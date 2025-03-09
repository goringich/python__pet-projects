import React, { useState, ChangeEvent, FormEvent } from 'react';
import { Container, Button, Stack, Typography } from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getRecords,
  addRecord,
  searchRecords,
  updateRecord,
  deleteRecord,
  getAge,
} from '../../api';
import { RecordData, FormFields, initialFormFields, ModalType } from './types';
import PhonebookTable from './PhonebookTable';
import ModalForm from './ModalForm';

const Phonebook: React.FC = () => {
  const queryClient = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery<RecordData[]>({
    queryKey: ['records'],
    queryFn: getRecords,
  });

  const addMutation = useMutation({
    mutationFn: addRecord,
    onSuccess: () => queryClient.invalidateQueries(['records']),
  });

  const searchMutation = useMutation({
    mutationFn: searchRecords,
  });

  const updateMutation = useMutation({
    mutationFn: updateRecord,
    onSuccess: () => queryClient.invalidateQueries(['records']),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRecord,
    onSuccess: () => queryClient.invalidateQueries(['records']),
  });

  const ageMutation = useMutation({
    mutationFn: getAge,
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<ModalType>(null);
  const [formFields, setFormFields] = useState<FormFields>({ ...initialFormFields });
  const [searchResults, setSearchResults] = useState<RecordData[] | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const openModal = (type: ModalType, prefill: Partial<FormFields> = {}) => {
    setModalType(type);
    setFormFields({ ...initialFormFields, ...prefill });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalType(null);
    setFormFields({ ...initialFormFields });
  };

  const handleFieldChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormFields((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log('Submitting form');
    console.log('Modal type:', modalType);
    console.log('Form fields:', formFields);

    try {
      switch (modalType) {
        case 'add':
          if (!formFields.Name || !formFields.Surname || !formFields.Phone) {
            showMessage('error', 'Name, Surname and Phone are required (обязательны)');
            console.log('Missing required fields for add');
            return;
          }
          await addMutation.mutateAsync({
            Name: formFields.Name,
            Surname: formFields.Surname,
            Phone: formFields.Phone,
            BirthDate: formFields.BirthDate,
          });
          showMessage('success', 'Record added successfully (запись успешно добавлена)');
          break;
        case 'search': {
          const results = await searchMutation.mutateAsync({
            Name: formFields.Name,
            Surname: formFields.Surname,
            Phone: formFields.Phone,
            BirthDate: formFields.BirthDate,
          });
          if (results && results.length > 0) {
            setSearchResults(results);
            showMessage('success', 'Search completed (поиск выполнен)');
          } else {
            showMessage('error', 'No records found (записи не найдены)');
          }
          break;
        }
        case 'update':
          if (!formFields.Name || !formFields.Surname || !formFields.Field || !formFields.NewValue) {
            showMessage('error', 'All fields are required to update (все поля обязательны для обновления)');
            return;
          }
          await updateMutation.mutateAsync({
            Name: formFields.Name,
            Surname: formFields.Surname,
            Field: formFields.Field,
            NewValue: formFields.NewValue,
          });
          showMessage('success', 'Record updated successfully (запись успешно обновлена)');
          break;
        case 'delete':
          if (!formFields.Name || !formFields.Surname) {
            showMessage('error', 'Name and Surname are required (обязательны)');
            return;
          }
          await deleteMutation.mutateAsync({
            Name: formFields.Name,
            Surname: formFields.Surname,
          });
          showMessage('success', 'Record deleted successfully (запись успешно удалена)');
          break;
        case 'age': {
          if (!formFields.Name || !formFields.Surname) {
            showMessage('error', 'Name and Surname are required (обязательны)');
            return;
          }
          const result = await ageMutation.mutateAsync({
            Name: formFields.Name,
            Surname: formFields.Surname,
          });
          if (result && result.age !== undefined) {
            showMessage('success', `Age: ${result.age} (возраст)`);
          } else {
            showMessage('error', 'Age information is unavailable (информация о возрасте недоступна)');
          }
          break;
        }
        default:
          console.log('No modal type specified');
          break;
      }
      closeModal();
      refetch();
    } catch (err: any) {
      console.error('Error in handleSubmit:', err);
      showMessage('error', err.response?.data?.error || 'An error occurred (произошла ошибка)');
    }
  };

  const handleDelete = async (record: RecordData) => {
    try {
      await deleteMutation.mutateAsync({
        Name: record.Name,
        Surname: record.Surname,
      });
      showMessage('success', 'Record deleted successfully (запись успешно удалена)');
      refetch();
    } catch (err: any) {
      showMessage('error', err.response?.data?.error || 'Error deleting record (ошибка удаления записи)');
    }
  };

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Dark Theme Phonebook
      </Typography>
      <Stack direction="row" spacing={2} justifyContent="center" sx={{ mb: 2 }}>
        <Button variant="contained" onClick={() => refetch()}>
          Load Records
        </Button>
        <Button variant="contained" onClick={() => openModal('add')}>
          Add Record
        </Button>
        <Button variant="contained" onClick={() => openModal('search')}>
          Search Records
        </Button>
        <Button variant="contained" onClick={() => openModal('delete')}>
          Delete Record
        </Button>
        <Button variant="contained" onClick={() => openModal('update')}>
          Update Record
        </Button>
        {/* <Button variant="contained" onClick={() => openModal('age')}>
          Show Age
        </Button> */}
      </Stack>

      {message && (
        <Typography variant="body1" align="center" color={message.type === 'success' ? 'green' : 'red'}>
          {message.text}
        </Typography>
      )}

      {isLoading && (
        <Typography variant="body1" align="center">
          Loading records...
        </Typography>
      )}

      {error && (
        <Typography variant="body1" align="center" color="red">
          Error loading records.
        </Typography>
      )}

      {data && (
        <PhonebookTable
          data={data}
          searchResults={searchResults}
          openModal={(type, prefill) => openModal(type, prefill)}
          deleteRecord={handleDelete}
        />
      )}

      <ModalForm
        modalOpen={modalOpen}
        modalType={modalType}
        formFields={formFields}
        handleFieldChange={handleFieldChange}
        handleSubmit={handleSubmit}
        closeModal={closeModal}
      />
    </Container>
  );
};

export default Phonebook;
