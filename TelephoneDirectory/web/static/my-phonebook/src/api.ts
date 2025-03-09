import { Record } from './types';

export async function makeRequest<T>(
  url: string,
  method: string,
  body: any = null
): Promise<T> {
  const options: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(JSON.stringify(data));
    }

    return data as T;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

export const getRecords = () =>
  makeRequest<Record[]>('/api/v1/users', 'GET');

export const addRecord = (record: Record) =>
  makeRequest<Record>('/api/v1/add', 'POST', record);

export const searchRecords = (criteria: Partial<Record>) =>
  makeRequest<Record[]>('/api/v1/search', 'POST', criteria);

export const updateRecord = (criteria: {
  Name: string;
  Surname: string;
  Field: string;
  NewValue: string;
}) =>
  makeRequest<{ success: boolean }>('/api/v1/update', 'PUT', criteria);

export const deleteRecord = (criteria: Pick<Record, 'Name' | 'Surname'>) =>
  makeRequest<{ success: boolean }>('/api/v1/delete', 'DELETE', criteria);

export const getAge = (criteria: Pick<Record, 'Name' | 'Surname'>) =>
  makeRequest<{ age: number }>('/api/v1/age', 'POST', criteria);

export function parseErrorMessage(error: any): string | null {
  try {
    const errorData = JSON.parse(error.message);
    return errorData.error || null;
  } catch (parseError) {
    console.error('Error parsing error message:', parseError);
    return null;
  }
}
