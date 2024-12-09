from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from flask_cors import CORS
from difflib import SequenceMatcher
import uuid

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) to allow requests from different origins
CORS(app)

# Define the filename for storing records
FILENAME = "bd.json"

# ----------------------------
# Data Persistence Functions
# ----------------------------

def load_data():
    """
    Load data from the JSON file.

    Returns:
        list: A list of record dictionaries. Returns an empty list if the file does not exist or is empty.
    """
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, 'r', encoding='utf-8') as f:
        if os.stat(FILENAME).st_size == 0:
            return []
        return json.load(f)

def save_data(data):
    """
    Save data to the JSON file.

    Args:
        data (list): A list of record dictionaries to be saved.
    """
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ----------------------------
# Validation Helper Functions
# ----------------------------

def format_name_surname(s):
    """
    Format the Name or Surname by stripping whitespace and capitalizing the first letter.

    Args:
        s (str): The string to format.

    Returns:
        str: The formatted string.
    """
    return s.strip().capitalize()

def valid_phone_number(num):
    """
    Validate and format the phone number.

    Converts phone numbers starting with '+7' to start with '8'.
    Ensures the phone number has exactly 11 digits.

    Args:
        num (str): The phone number string.

    Returns:
        str or None: The formatted phone number if valid, else None.
    """
    num = num.strip()
    if num.startswith('+7'):
        num = '8' + num[2:]
    if len(num) == 11 and num.isdigit():
        return num
    return None

def valid_date(d):
    """
    Validate and format the birth date.

    Args:
        d (str): The date string in 'DD.MM.YYYY' format.

    Returns:
        str or None: The formatted date string if valid, empty string if not provided, else None.
    """
    d = d.strip()
    if d == '':
        return ''
    try:
        # Ensure the date is in the correct format
        return datetime.strptime(d, '%d.%m.%Y').strftime('%d.%m.%Y')
    except ValueError:
        return None

# ----------------------------
# API Endpoints
# ----------------------------

@app.route('/records', methods=['GET'])
def get_records():
    """
    Retrieve all records.

    Returns:
        Response: JSON list of all records with HTTP status 200.
    """
    data = load_data()
    return jsonify(data), 200

def is_similar(a, b, threshold=0.8):
    """
    Determine if two strings are similar based on a threshold.

    Uses SequenceMatcher to compute the similarity ratio.

    Args:
        a (str): First string.
        b (str): Second string.
        threshold (float): Similarity threshold.

    Returns:
        bool: True if similarity ratio >= threshold, else False.
    """
    return SequenceMatcher(None, a, b).ratio() >= threshold

@app.route('/search', methods=['POST'])
def search_records():
    """
    Search records based on provided criteria.

    Supports partial and approximate matches for Name and Surname.

    Returns:
        Response: JSON list of matching records with HTTP status 200.
    """
    criteria = request.json
    data = load_data()
    results = []
    for rec in data:
        match = True
        # Check Name similarity
        if 'Name' in criteria and criteria['Name']:
            if not is_similar(criteria['Name'].strip().lower(), rec['Name'].strip().lower()):
                match = False
        # Check Surname similarity
        if 'Surname' in criteria and criteria['Surname']:
            if not is_similar(criteria['Surname'].strip().lower(), rec['Surname'].strip().lower()):
                match = False
        # Check exact Phone match
        if 'Phone' in criteria and criteria['Phone']:
            if criteria['Phone'].strip() != rec['Phone'].strip():
                match = False
        # Check exact BirthDate match
        if 'BirthDate' in criteria and criteria['BirthDate']:
            if criteria['BirthDate'].strip() != rec['BirthDate'].strip():
                match = False
        if match:
            results.append(rec)
    return jsonify(results), 200

@app.route('/add', methods=['POST'])
def add_record():
    """
    Add a new record to the database.

    Validates input data and checks for duplicates based on ID or Name and Surname.

    Returns:
        Response: JSON message with HTTP status 201 on success,
                  400 for invalid input,
                  409 for duplicate records.
    """
    data = load_data()
    new_record = request.json

    # Validate inputs
    name = format_name_surname(new_record.get('Name', ''))
    surname = format_name_surname(new_record.get('Surname', ''))
    phone = valid_phone_number(new_record.get('Phone', ''))
    birth_date = valid_date(new_record.get('BirthDate', ''))

    if not name or not surname or not phone:
        return jsonify({'error': 'Invalid input. Name, Surname, and Phone are required.'}), 400

    # Check for duplicates by unique ID (if provided)
    if 'ID' in new_record:
        for rec in data:
            if rec.get('ID') == new_record['ID']:
                return jsonify({
                    'error': 'Duplicate record by ID. A record with this ID already exists.',
                    'existing_record': rec
                }), 409
    else:
        # Check for duplicates by Name and Surname
        for rec in data:
            if rec['Name'].lower() == name.lower() and rec['Surname'].lower() == surname.lower():
                return jsonify({
                    'error': 'Duplicate record by Name and Surname. A record with the same Name and Surname already exists.',
                    'existing_record': rec
                }), 409

    # Generate unique ID for the new record
    record_id = str(uuid.uuid4())
    record = {
        'ID': record_id,
        'Name': name,
        'Surname': surname,
        'Phone': phone,
        'BirthDate': birth_date if birth_date else ""
    }

    # Append the new record and save
    data.append(record)
    save_data(data)
    return jsonify({'message': "Record added successfully", 'record': record}), 201

@app.route('/delete', methods=['POST'])
def delete_record():
    """
    Delete a record based on Name and Surname.

    Args:
        JSON payload containing 'Name' and 'Surname'.

    Returns:
        Response: JSON message with HTTP status 200 on success,
                  400 for missing fields,
                  404 if record not found.
    """
    data = load_data()
    criteria = request.json

    name = format_name_surname(criteria.get('Name', ''))
    surname = format_name_surname(criteria.get('Surname', ''))

    if not name or not surname:
        return jsonify({'error': 'Name and Surname are required to delete a record.'}), 400

    # Filter out the record to be deleted
    new_data = [rec for rec in data if not (rec['Name'].lower() == name.lower() and rec['Surname'].lower() == surname.lower())]

    if len(new_data) == len(data):
        # No record was deleted
        return jsonify({'error': 'Record not found.'}), 404

    # Save the updated data
    save_data(new_data)
    return jsonify({'message': 'Record deleted successfully.'}), 200

@app.route('/update', methods=['PUT'])
def update_record():
    """
    Update a specific field in a record identified by Name and Surname.

    Args:
        JSON payload containing 'Name', 'Surname', 'Field', and 'NewValue'.

    Returns:
        Response: JSON message with HTTP status 200 on success,
                  400 for invalid input,
                  404 if record not found.
    """
    data = load_data()
    criteria = request.json

    print("Update criteria received:", criteria)  # For debugging purposes

    # Extract and normalize Name and Surname from criteria
    name = criteria.get('Name', '').strip().lower()
    surname = criteria.get('Surname', '').strip().lower()

    # Locate the record to update
    record_to_update = None
    for record in data:
        if record['Name'].lower() == name and record['Surname'].lower() == surname:
            record_to_update = record
            break

    if not record_to_update:
        return jsonify({'error': 'Record not found.'}), 404

    # Extract the field to update and the new value
    field_to_update = criteria.get('Field', '').lower()
    new_value = criteria.get('NewValue', '').strip()

    if not field_to_update or not new_value:
        return jsonify({'error': 'Field and NewValue are required.'}), 400

    # Update the appropriate field with validation
    if field_to_update == 'name':
        record_to_update['Name'] = format_name_surname(new_value)
    elif field_to_update == 'surname':
        record_to_update['Surname'] = format_name_surname(new_value)
    elif field_to_update == 'phone':
        valid_phone = valid_phone_number(new_value)
        if not valid_phone:
            return jsonify({'error': 'Invalid phone number.'}), 400
        record_to_update['Phone'] = valid_phone
    elif field_to_update == 'birthdate':
        valid_bd = valid_date(new_value)
        if valid_bd is None:
            return jsonify({'error': 'Invalid birth date.'}), 400
        record_to_update['BirthDate'] = valid_bd
    else:
        return jsonify({'error': 'Invalid field to update.'}), 400

    # Save the updated data
    save_data(data)
    print("Record updated successfully:", record_to_update)  # For debugging purposes
    return jsonify({'message': 'Record updated successfully.'}), 200

@app.route('/age', methods=['POST'])
def get_age():
    """
    Calculate the age of a person based on their birth date.

    Args:
        JSON payload containing 'Name' and 'Surname'.

    Returns:
        Response: JSON with the calculated age and HTTP status 200 on success,
                  400 for missing fields or invalid birth date,
                  404 if record not found.
    """
    criteria = request.json
    data = load_data()
    name = format_name_surname(criteria.get('Name', ''))
    surname = format_name_surname(criteria.get('Surname', ''))

    if not name or not surname:
        return jsonify({'error': 'Name and Surname are required to calculate age.'}), 400

    # Locate the record
    for rec in data:
        if rec['Name'].lower() == name.lower() and rec['Surname'].lower() == surname.lower():
            if not rec['BirthDate']:
                return jsonify({'error': 'Birth date not available for this record.'}), 400
            try:
                # Parse the birth date
                birth_date = datetime.strptime(rec['BirthDate'], '%d.%m.%Y')
                today = datetime.today()
                # Calculate age
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return jsonify({'age': age}), 200
            except ValueError:
                return jsonify({'error': 'Invalid birth date format in record.'}), 400

    # Record not found
    return jsonify({'error': 'Record not found.'}), 404

# ----------------------------
# Application Entry Point
# ----------------------------

if __name__ == "__main__":
    # Run the Flask application in debug mode for development purposes
    app.run(debug=True)
