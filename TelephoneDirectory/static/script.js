// DOM Elements
const loadButton = document.getElementById('load');
const addButton = document.getElementById('add');
const searchButton = document.getElementById('search');
const deleteButton = document.getElementById('delete');
const updateButton = document.getElementById('update');
const ageButton = document.getElementById('age');
const recordsTable = document.getElementById('records');
const errorDiv = document.getElementById('error-message');
const successDiv = document.getElementById('success-message');
const modal = document.getElementById('modal');
const modalBody = document.getElementById('modal-body');
const spanClose = document.getElementsByClassName('close')[0];

// Close modal when 'x' is clicked
spanClose.onclick = closeModal;

// Close modal when clicking outside of the modal
window.onclick = function (event) {
  if (event.target === modal) closeModal();
};

/**
 * Closes the modal and clears its content.
 */
function closeModal() {
  modal.style.display = 'none';
  modalBody.innerHTML = '';
}

/**
 * Displays a message to the user.
 * @param {string} type - Type of message ('error' or 'success').
 * @param {string} message - The message content.
 */
function showMessage(type, message) {
  const messageDiv = type === 'error' ? errorDiv : successDiv;
  const oppositeDiv = type === 'error' ? successDiv : errorDiv;

  messageDiv.style.display = 'block';
  oppositeDiv.style.display = 'none';
  messageDiv.textContent = message;

  // Hide the message after 5 seconds
  setTimeout(() => {
    messageDiv.style.display = 'none';
  }, 5000);
}

/**
 * Makes an API request.
 * @param {string} url - The API endpoint.
 * @param {string} method - HTTP method ('GET', 'POST', 'PUT', etc.).
 * @param {Object|null} body - The request payload.
 * @returns {Promise<Object>} - The response data.
 */
async function makeRequest(url, method, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) options.body = JSON.stringify(body);

  try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(JSON.stringify(data));
    }
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

/**
 * Displays records in the table.
 * @param {Array} data - Array of record objects.
 */
function displayRecords(data) {
  recordsTable.innerHTML = '';

  if (!Array.isArray(data) || data.length === 0) {
    recordsTable.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
    return;
  }

  // Create table headers if not present
  if (recordsTable.tHead === null) {
    const header = recordsTable.createTHead();
    const headerRow = header.insertRow();
    const headers = ['Name', 'Surname', 'Phone', 'Birth Date', 'Actions'];
    headers.forEach(text => {
      const th = document.createElement('th');
      th.textContent = text;
      headerRow.appendChild(th);
    });
  }

  const tbody = recordsTable.tBodies[0] || recordsTable.createTBody();

  data.forEach(record => {
    const row = tbody.insertRow();
    row.innerHTML = `
      <td>${sanitizeHTML(record.Name)}</td>
      <td>${sanitizeHTML(record.Surname)}</td>
      <td>${sanitizeHTML(record.Phone)}</td>
      <td>${sanitizeHTML(record.BirthDate) || 'N/A'}</td>
      <td>
        <button class="edit-btn" data-name="${encodeURIComponent(record.Name)}" data-surname="${encodeURIComponent(record.Surname)}">Edit</button>
        <button class="delete-btn" data-name="${encodeURIComponent(record.Name)}" data-surname="${encodeURIComponent(record.Surname)}">Delete</button>
      </td>
    `;
  });

  // Attach event listeners to newly created buttons
  attachRowEventListeners();
}

/**
 * Sanitizes input to prevent XSS attacks.
 * @param {string} str - The string to sanitize.
 * @returns {string} - Sanitized string.
 */
function sanitizeHTML(str) {
  const temp = document.createElement('div');
  temp.textContent = str;
  return temp.innerHTML;
}

/**
 * Attaches event listeners to Edit and Delete buttons within the table.
 */
function attachRowEventListeners() {
  // Edit buttons
  const editButtons = recordsTable.querySelectorAll('.edit-btn');
  editButtons.forEach(button => {
    button.removeEventListener('click', editRecordHandlerDirect); // Prevent duplicate listeners
    button.addEventListener('click', editRecordHandlerDirect);
  });

  // Delete buttons
  const deleteButtons = recordsTable.querySelectorAll('.delete-btn');
  deleteButtons.forEach(button => {
    button.removeEventListener('click', deleteRecordDirectHandler); // Prevent duplicate listeners
    button.addEventListener('click', deleteRecordDirectHandler);
  });
}

/**
 * Handles the Edit Record button click event.
 * @param {Event} event - The click event.
 */
async function editRecordHandlerDirect(event) {
  const name = decodeURIComponent(event.target.getAttribute('data-name'));
  const surname = decodeURIComponent(event.target.getAttribute('data-surname'));

  generateModalForm(
    [
      { id: 'edit-field', label: 'Field to Update', placeholder: 'Enter field (Name, Surname, Phone, BirthDate)', type: 'text', required: true },
      { id: 'edit-value', label: 'New Value', placeholder: 'Enter new value', type: 'text', required: true },
    ],
    'Update Record',
    async () => {
      const field = document.getElementById('edit-field').value.trim();
      const newValue = document.getElementById('edit-value').value.trim();

      if (!field || !newValue) {
        showMessage('error', 'Field and New Value are required.');
        return;
      }

      const criteria = { Name: name, Surname: surname, Field: field, NewValue: newValue };

      console.log('Updating record with criteria:', criteria);

      try {
        await makeRequest('http://127.0.0.1:5000/update', 'PUT', criteria);
        showMessage('success', 'Record updated successfully.');
        closeModal();
        loadRecords();
      } catch (error) {
        console.error('Update error:', error);
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Failed to update record.');
      }
    }
  );
}

/**
 * Handles the Delete Record button click event directly from the table.
 * @param {Event} event - The click event.
 */
function deleteRecordDirectHandler(event) {
  const name = decodeURIComponent(event.target.getAttribute('data-name'));
  const surname = decodeURIComponent(event.target.getAttribute('data-surname'));

  const criteria = { Name: name, Surname: surname };

  if (confirm(`Are you sure you want to delete ${name} ${surname}?`)) {
    makeRequest('http://127.0.0.1:5000/delete', 'POST', criteria)
      .then(() => {
        showMessage('success', 'Record deleted successfully.');
        loadRecords();
      })
      .catch(error => {
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Error deleting record.');
      });
  }
}

/**
 * Loads all records from the server and displays them.
 */
async function loadRecords() {
  try {
    const data = await makeRequest('http://127.0.0.1:5000/records', 'GET');
    displayRecords(data);
    showMessage('success', 'Records loaded successfully.');
  } catch (error) {
    showMessage('error', 'Error loading records.');
  }
}

/**
 * Generates a modal form based on provided fields.
 * @param {Array} fields - Array of field objects for the form.
 * @param {string} buttonLabel - Label for the submit button.
 * @param {Function} onSubmit - Callback function to execute on form submission.
 */
function generateModalForm(fields, buttonLabel, onSubmit) {
  // Generate form fields
  const formFields = fields
    .map(field => {
      if (field.type === 'select') {
        const options = field.options
          .map(option => `<option value="${option.value}">${option.text}</option>`)
          .join('');
        return `
          <div class="form-group">
            <label for="${field.id}">${field.label}</label>
            <select id="${field.id}" ${field.required ? 'required' : ''}>
              ${options}
            </select>
          </div>
        `;
      } else {
        return `
          <div class="form-group">
            <label for="${field.id}">${field.label}</label>
            <input type="${field.type}" id="${field.id}" placeholder="${field.placeholder}" ${field.required ? 'required' : ''}>
          </div>
        `;
      }
    })
    .join('');

  // Set modal content
  modalBody.innerHTML = `
    <form id="modal-form">
      ${formFields}
      <button type="submit" id="modal-submit">${buttonLabel}</button>
    </form>
  `;
  modal.style.display = 'block';

  // Attach submit event listener
  document.getElementById('modal-form').addEventListener('submit', function (e) {
    e.preventDefault();
    onSubmit();
  });
}

/**
 * Handles the Add Record button click event.
 */
function addRecordHandler() {
  generateModalForm(
    [
      { id: 'name', label: 'Name', placeholder: 'Enter first name', type: 'text', required: true },
      { id: 'surname', label: 'Surname', placeholder: 'Enter surname', type: 'text', required: true },
      { id: 'phone', label: 'Phone', placeholder: 'Enter phone number', type: 'text', required: true },
      { id: 'birthdate', label: 'Birth Date', placeholder: 'Enter birth date (DD.MM.YYYY)', type: 'date' },
    ],
    'Add Record',
    async () => {
      const name = document.getElementById('name').value.trim();
      const surname = document.getElementById('surname').value.trim();
      const phone = document.getElementById('phone').value.trim();
      const birthdate = document.getElementById('birthdate').value.trim();

      if (!name || !surname || !phone) {
        showMessage('error', 'Name, Surname, and Phone are required.');
        return;
      }

      const record = { Name: name, Surname: surname, Phone: phone, BirthDate: birthdate };

      try {
        await makeRequest('http://127.0.0.1:5000/add', 'POST', record);
        showMessage('success', 'Record added successfully.');
        closeModal();
        loadRecords();
      } catch (error) {
        handleAddRecordError(error);
      }
    }
  );
}

/**
 * Handles errors specifically for the Add Record operation.
 * @param {Error} error - The error object.
 */
function handleAddRecordError(error) {
  try {
    const errorData = JSON.parse(error.message);
    if (errorData.error && errorData.error.includes('Duplicate record')) {
      const existingRecord = errorData.existing_record;

      closeModal();

      generateModalForm(
        [
          {
            id: 'action',
            label: 'Choose Action',
            type: 'select',
            options: [
              { value: 'edit_existing', text: 'Edit Existing Record' },
              { value: 'change_new', text: 'Change Name/Surname of New Record' },
              { value: 'cancel', text: 'Cancel and Return to Menu' },
            ],
          },
        ],
        'Duplicate Record Found',
        async () => {
          const action = document.getElementById('action').value;
          if (action === 'edit_existing') {
            editExistingRecord(existingRecord);
          } else if (action === 'change_new') {
            addRecordHandler();
          } else {
            closeModal();
          }
        }
      );
    } else {
      showMessage('error', errorData.error || 'Failed to add record.');
    }
  } catch (parseError) {
    console.error('Error parsing add record error:', parseError);
    showMessage('error', 'Failed to add record.');
  }
}

/**
 * Initiates editing of an existing record.
 * @param {Object} record - The existing record object.
 */
function editExistingRecord(record) {
  generateModalForm(
    [
      { id: 'edit-field', label: 'Field to Update', placeholder: 'Enter field (Name, Surname, Phone, BirthDate)', type: 'text', required: true },
      { id: 'edit-value', label: 'New Value', placeholder: 'Enter new value', type: 'text', required: true },
    ],
    'Edit Existing Record',
    async () => {
      const field = document.getElementById('edit-field').value.trim();
      const newValue = document.getElementById('edit-value').value.trim();

      if (!field || !newValue) {
        showMessage('error', 'Field and New Value are required.');
        return;
      }

      const updateCriteria = { ID: record.ID, Field: field, NewValue: newValue };

      try {
        await makeRequest('http://127.0.0.1:5000/update', 'PUT', updateCriteria);
        showMessage('success', 'Existing record updated successfully.');
        closeModal();
        loadRecords();
      } catch (error) {
        console.error('Error updating existing record:', error);
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Failed to update existing record.');
      }
    }
  );
}

/**
 * Handles the Search Record button click event.
 */
function searchRecordHandler() {
  generateModalForm(
    [
      { id: 'search-name', label: 'Name', placeholder: 'Enter first name', type: 'text' },
      { id: 'search-surname', label: 'Surname', placeholder: 'Enter surname', type: 'text' },
      { id: 'search-phone', label: 'Phone', placeholder: 'Enter phone number', type: 'text' },
      { id: 'search-birthdate', label: 'Birth Date', placeholder: 'Enter birth date (DD.MM.YYYY)', type: 'date' },
    ],
    'Search Records',
    async () => {
      const criteria = {
        Name: document.getElementById('search-name').value.trim(),
        Surname: document.getElementById('search-surname').value.trim(),
        Phone: document.getElementById('search-phone').value.trim(),
        BirthDate: document.getElementById('search-birthdate').value.trim(),
      };

      try {
        const data = await makeRequest('http://127.0.0.1:5000/search', 'POST', criteria);
        if (Array.isArray(data) && data.length > 0) {
          displayRecords(data);
          showMessage('success', 'Search completed.');
        } else {
          showMessage('error', 'No records found.');
        }
        closeModal();
      } catch (error) {
        console.error('Search error:', error);
        showMessage('error', 'Error searching records.');
      }
    }
  );
}

/**
 * Handles the Delete Record button click event.
 */
function deleteRecordHandler() {
  generateModalForm(
    [
      { id: 'delete-name', label: 'Name', placeholder: 'Enter first name', type: 'text', required: true },
      { id: 'delete-surname', label: 'Surname', placeholder: 'Enter surname', type: 'text', required: true },
    ],
    'Delete Record',
    async () => {
      const criteria = {
        Name: document.getElementById('delete-name').value.trim(),
        Surname: document.getElementById('delete-surname').value.trim(),
      };

      try {
        await makeRequest('http://127.0.0.1:5000/delete', 'POST', criteria);
        showMessage('success', 'Record deleted successfully.');
        closeModal();
        loadRecords();
      } catch (error) {
        console.error('Delete error:', error);
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Error deleting record.');
      }
    }
  );
}

/**
 * Handles the Update Record button click event.
 */
function updateRecordHandler() {
  generateModalForm(
    [
      { id: 'update-name', label: 'Current Name', placeholder: 'Enter current first name', type: 'text', required: true },
      { id: 'update-surname', label: 'Current Surname', placeholder: 'Enter current surname', type: 'text', required: true },
      { id: 'update-field', label: 'Field to Update', placeholder: 'Enter field name (Name, Surname, Phone, BirthDate)', type: 'text', required: true },
      { id: 'update-value', label: 'New Value', placeholder: 'Enter new value', type: 'text', required: true },
    ],
    'Update Record',
    async () => {
      const name = document.getElementById('update-name').value.trim();
      const surname = document.getElementById('update-surname').value.trim();
      const field = document.getElementById('update-field').value.trim();
      const newValue = document.getElementById('update-value').value.trim();

      if (!name || !surname || !field || !newValue) {
        showMessage('error', 'All fields are required to update a record.');
        return;
      }

      // Validate allowed fields
      const allowedFields = ['Name', 'Surname', 'Phone', 'BirthDate'];
      if (!allowedFields.includes(field)) {
        showMessage('error', `Invalid field. Allowed fields: ${allowedFields.join(', ')}`);
        return;
      }

      const criteria = { Name: name, Surname: surname, Field: field, NewValue: newValue };

      try {
        await makeRequest('http://127.0.0.1:5000/update', 'PUT', criteria);
        showMessage('success', 'Record updated successfully.');
        closeModal();
        loadRecords();
      } catch (error) {
        console.error('Update error:', error);
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Failed to update record.');
      }
    }
  );
}

/**
 * Handles the Calculate Age button click event.
 */
function showAgeHandler() {
  generateModalForm(
    [
      { id: 'age-name', label: 'Name', placeholder: 'Enter first name', type: 'text', required: true },
      { id: 'age-surname', label: 'Surname', placeholder: 'Enter surname', type: 'text', required: true },
    ],
    'Calculate Age',
    async () => {
      const criteria = {
        Name: document.getElementById('age-name').value.trim(),
        Surname: document.getElementById('age-surname').value.trim(),
      };

      try {
        const result = await makeRequest('http://127.0.0.1:5000/age', 'POST', criteria);
        if (result.age !== undefined) {
          showMessage('success', `Age: ${result.age}`);
        } else {
          showMessage('error', 'Age information is unavailable.');
        }
        closeModal();
      } catch (error) {
        console.error('Age calculation error:', error);
        const errorMsg = parseErrorMessage(error);
        showMessage('error', errorMsg || 'Error calculating age.');
      }
    }
  );
}

/**
 * Parses error messages from the server response.
 * @param {Error} error - The error object.
 * @returns {string|null} - Parsed error message or null.
 */
function parseErrorMessage(error) {
  try {
    const errorData = JSON.parse(error.message);
    return errorData.error || null;
  } catch (parseError) {
    console.error('Error parsing error message:', parseError);
    return null;
  }
}

// Event listeners for main buttons
loadButton.addEventListener('click', loadRecords);
addButton.addEventListener('click', addRecordHandler);
searchButton.addEventListener('click', searchRecordHandler);
deleteButton.addEventListener('click', deleteRecordHandler);
updateButton.addEventListener('click', updateRecordHandler);
ageButton.addEventListener('click', showAgeHandler);
