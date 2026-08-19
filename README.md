# Face Authentication & Attendance System

A Streamlit application that provides:

- Face-based user registration
- One face = one account
- Duplicate face prevention
- Face-based login
- Face-based logout
- Login/logout timestamps
- SQLite attendance database
- Attendance dashboard

## Project Structure

```text
Face_Authentication_System/
├── app.py
├── config.py
├── database.py
├── face_utils.py
├── validators.py
├── requirements.txt
├── .gitignore
├── README.md
└── data/
    └── face_auth.db
```

## Installation

Python 3.10 or 3.11 is recommended for easier installation of `face-recognition` and its native dependency.

Create an environment:

```powershell
py -3.10 -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Test face recognition:

```powershell
python -c "import face_recognition; print('face_recognition OK')"
```

Run:

```powershell
python -m streamlit run app.py
```
**How it works**

### Registration

1. User enters name, email and employee ID.
2. User captures one face.
3. The application detects faces.
4. Registration is rejected if zero or multiple faces are detected.
5. A 128-dimensional face encoding is generated.
6. The new encoding is compared with every existing account.
7. If the face is already registered, registration is rejected.
8. Otherwise the user and face encoding are saved to SQLite.

### Login

1. User captures a face.
2. The face encoding is generated.
3. It is compared against registered encodings.
4. The closest match is selected.
5. The match is accepted only when its distance is below the configured tolerance.
6. Login time is stored in the attendance table.

### Logout

The same face-matching process is used. The latest active attendance record is updated with the logout time.

## Face Matching

The application uses the `face_recognition` library.

Face encodings are 128-dimensional vectors. Matching is performed using face distance.

The default threshold is:

```python
FACE_MATCH_TOLERANCE = 0.5
```

A lower threshold is stricter. A higher threshold is more permissive.

For production use, test the threshold with representative lighting, camera quality and users.

## Database

SQLite stores:

### users

- id
- name
- email
- employee_id
- face_encoding
- created_at

### attendance

- id
- user_id
- login_time
- logout_time

The face encoding is stored as a BLOB.
