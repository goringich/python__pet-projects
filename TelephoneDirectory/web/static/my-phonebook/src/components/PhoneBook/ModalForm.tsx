import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
} from '@mui/material';
import { ModalType, FormFields } from './types';

interface ModalFormProps {
  modalOpen: boolean;
  modalType: ModalType;
  formFields: FormFields;
  handleFieldChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent) => void;
  closeModal: () => void;
}

const ModalForm: React.FC<ModalFormProps> = ({
  modalOpen,
  modalType,
  formFields,
  handleFieldChange,
  handleSubmit,
  closeModal,
}) => {
  const renderModalFields = () => {
    switch (modalType) {
      case 'add':
        return (
          <>
            <TextField
              margin="dense"
              label="Name"
              name="Name"
              fullWidth
              required
              value={formFields.Name}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Surname"
              name="Surname"
              fullWidth
              required
              value={formFields.Surname}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Phone"
              name="Phone"
              fullWidth
              required
              value={formFields.Phone}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Birth Date (DD.MM.YYYY)"
              name="BirthDate"
              fullWidth
              value={formFields.BirthDate}
              onChange={handleFieldChange}
            />
          </>
        );
      case 'search':
        return (
          <>
            <TextField
              margin="dense"
              label="Name"
              name="Name"
              fullWidth
              value={formFields.Name}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Surname"
              name="Surname"
              fullWidth
              value={formFields.Surname}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Phone"
              name="Phone"
              fullWidth
              value={formFields.Phone}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Birth Date (DD.MM.YYYY)"
              name="BirthDate"
              fullWidth
              value={formFields.BirthDate}
              onChange={handleFieldChange}
            />
          </>
        );
      case 'update':
        return (
          <>
            <Typography variant="body2" gutterBottom>
              Enter current Name and Surname to identify the record and specify which field to update.
            </Typography>
            <TextField
              margin="dense"
              label="Name"
              name="Name"
              fullWidth
              required
              value={formFields.Name}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Surname"
              name="Surname"
              fullWidth
              required
              value={formFields.Surname}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Field to Update (Name, Surname, Phone, BirthDate)"
              name="Field"
              fullWidth
              required
              value={formFields.Field}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="New Value"
              name="NewValue"
              fullWidth
              required
              value={formFields.NewValue}
              onChange={handleFieldChange}
            />
          </>
        );
      case 'delete':
        return (
          <>
            <TextField
              margin="dense"
              label="Name"
              name="Name"
              fullWidth
              required
              value={formFields.Name}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Surname"
              name="Surname"
              fullWidth
              required
              value={formFields.Surname}
              onChange={handleFieldChange}
            />
          </>
        );
      case 'age':
        return (
          <>
            <TextField
              margin="dense"
              label="Name"
              name="Name"
              fullWidth
              required
              value={formFields.Name}
              onChange={handleFieldChange}
            />
            <TextField
              margin="dense"
              label="Surname"
              name="Surname"
              fullWidth
              required
              value={formFields.Surname}
              onChange={handleFieldChange}
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={modalOpen} onClose={closeModal} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {modalType === 'add' && 'Add Record'}
          {modalType === 'search' && 'Search Records'}
          {modalType === 'update' && 'Update Record'}
          {modalType === 'delete' && 'Delete Record'}
          {modalType === 'age' && 'Calculate Age'}
        </DialogTitle>
        <DialogContent dividers>{renderModalFields()}</DialogContent>
        <DialogActions>
          <Button onClick={closeModal}>Cancel</Button>
          <Button type="submit">
            {modalType === 'add' && 'Add'}
            {modalType === 'search' && 'Search'}
            {modalType === 'update' && 'Update'}
            {modalType === 'delete' && 'Delete'}
            {modalType === 'age' && 'Calculate'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ModalForm;
