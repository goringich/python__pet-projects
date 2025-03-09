export interface RecordData {
  Name: string;
  Surname: string;
  Phone: string;
  BirthDate?: string;
}

export type ModalType = 'add' | 'search' | 'update' | 'delete' | 'age' | null;

export interface FormFields {
  [key: string]: string;
}

export const initialFormFields: FormFields = {
  Name: '',
  Surname: '',
  Phone: '',
  BirthDate: '',
  Field: '',
  NewValue: '',
};
