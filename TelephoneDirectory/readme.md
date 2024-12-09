# Phonebook Management System

![image](https://github.com/user-attachments/assets/0f455ddb-aa27-4bb3-bd85-ad70d2a2ee00)


This is a simple web-based phonebook application built with **HTML**, **CSS**, **JavaScript**, and **Flask**. It allows you to manage records by adding, searching, updating, deleting, and calculating the age of individuals based on their birthdate.

---

## **Features**

![image](https://github.com/user-attachments/assets/fe2d667a-03d8-4510-836e-6182a7c8545d)

1. View all phonebook records in a neat table.
2. Add a new record with:
   - **Name** (required)
   - **Surname** (required)
   - **Phone** (required, 11 digits)
   - **Birthdate** (optional, format: DD.MM.YYYY)
3. Search for records by:
   - Name
   - Surname
   - Phone
   - Birthdate
4. Update specific details of an existing record.
5. Delete a record using its name and surname.
6. Calculate the age of an individual based on their birthdate.

---

## **Technologies Used**

- **Frontend**: HTML, CSS (Dark Theme), JavaScript (Fetch API)
- **Backend**: Flask (Python)
- **Data Storage**: JSON file

---

## **How to Run**

### Prerequisites:
- Python 3.8+ installed.
- A package manager like `pip`.
- A terminal or command line tool (e.g., CMD, PowerShell, Linux Terminal).

### Steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/phonebook-system.git
   cd phonebook-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows (CMD):
     ```bash
     venv\Scripts\activate
     ```
   - On Windows (PowerShell):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the Flask server:
   ```bash
   python app.py
   ```

6. Open the application in your browser:
   Navigate to `http://127.0.0.1:5000`.

---

## **Project Structure**

```
├── static/
│   ├── css/
│   │   └── styles.css       # Dark theme styles
│   ├── js/
│   │   └── script.js        # Main JavaScript logic
├── templates/
│   └── index.html           # Main HTML file
├── app.py                   # Flask backend application
├── bd.json                  # JSON file storing records
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```







