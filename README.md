# SmartPresence
 
AI-powered classroom attendance system that recognises students from **face** and **voice**, built with Streamlit and backed by Supabase (Postgres).
 
Created with ❤️ by Divyesh Puranik
 
---
 
## Overview
 
SmartPresence gives a class two portals — **Teacher** and **Student** — inside a single Streamlit app:
 
- Teachers create subjects, share a join code / QR link, and take attendance by scanning classroom **photos** (facial recognition) or a classroom **audio recording** (voice recognition).
- Students log in with their face (no password), optionally enroll their voice, join subjects with a code or QR link, and track their own attendance.
All recognition runs locally in the app process (dlib + scikit-learn for faces, Resemblyzer + librosa for voice); Supabase stores users, subjects, enrollments and attendance logs.
 
## Features
 
**Teacher portal**
- Register / login with a username + bcrypt-hashed password
- Create subjects (code, name, section)
- Share a subject via a join code and an auto-generated QR code
- Take attendance two ways:
  - **Face mode** — capture or upload classroom photos, auto-detect and match every face
  - **Voice mode** — record classroom audio, auto-segment and match every speaker
- Review and confirm results before they're saved
- View attendance records grouped by session, with a present/total summary per class
**Student portal**
- Register by capturing a face photo (creates a 128-d face embedding)
- Optional voice enrollment (short recorded phrase) for voice-based attendance
- Face-ID login — no password, just the camera
- Enroll in subjects via join code, QR scan, or an auto-enroll link (`?join_code=...`)
- View enrolled subjects with attendance stats, and unenroll if needed
## Architecture
 
```mermaid
flowchart TD
    Client["Browser client<br/>teacher / student"]
    App["Streamlit app (app.py)<br/>session-state router"]
    Home["Home screen<br/>choose portal"]
    Teacher["Teacher screen<br/>login/register, dashboard"]
    Student["Student screen<br/>face-ID login/register, dashboard"]
    Dialogs["Dialog components<br/>create subject, enroll, add photos,<br/>share (QR), voice attendance, results"]
    FaceP["Face pipeline<br/>dlib detector + shape predictor<br/>+ SVM classifier (scikit-learn)"]
    VoiceP["Voice pipeline<br/>Resemblyzer VoiceEncoder<br/>+ librosa segmentation"]
    DB[("Supabase / Postgres<br/>teachers, students, subjects,<br/>subject_students, attendance_logs")]
 
    Client --> App
    App --> Home
    App --> Teacher
    App --> Student
    Teacher --> Dialogs
    Student --> Dialogs
    Teacher --> FaceP
    Teacher --> VoiceP
    Student --> FaceP
    Student --> VoiceP
    FaceP --> DB
    VoiceP --> DB
    Teacher --> DB
    Student --> DB
```
 
The app is a single Streamlit process — there is no separate backend service. `st.session_state` acts as the in-memory session/router, `src/screens/database/db.py` talks to Supabase directly, and the two pipelines are cached in-process with `@st.cache_resource`.
 
## Core flows
 
### Taking attendance (teacher)
 
```mermaid
flowchart TD
    A[Teacher selects a subject] --> B{Attendance mode}
    B -->|Face| C[Capture / upload classroom photos]
    B -->|Voice| D[Record classroom audio]
    C --> E["Face pipeline: detect faces,<br/>classify with trained SVM"]
    D --> F["Voice pipeline: split audio into<br/>segments, match voice embeddings"]
    E --> G[Compare detected students against<br/>subject_students enrollment]
    F --> G
    G --> H[Show present / absent results]
    H -->|Confirm| I[("Insert rows into attendance_logs")]
    H -->|Discard| J[Discard, try again]
```
 
### Student registration & login
 
```mermaid
flowchart TD
    A[Student opens camera] --> B["Face pipeline extracts<br/>128-d face embedding (dlib)"]
    B --> C{Matches an<br/>existing student?}
    C -->|Yes, within threshold| D[Log in as that student]
    C -->|No match| E[Show registration form]
    E --> F[Optional: record a short voice sample]
    F --> G["Voice pipeline extracts<br/>voice embedding (Resemblyzer)"]
    G --> H[("Create student record in Supabase")]
    H --> I[Retrain SVM classifier<br/>with the new embedding]
    I --> D
```
 
### Recognition thresholds
- **Face match**: a linear SVM (scikit-learn) is trained on every stored face embedding; a prediction is only accepted if the Euclidean distance to that student's stored embedding is ≤ **0.6**.
- **Voice match**: cosine similarity between the new embedding and a candidate's stored embedding must be ≥ **0.65** to count as a match. For classroom (bulk) audio, the recording is split into speech segments with `librosa.effects.split`, and each segment is matched independently so several speakers can be identified from one recording.
## Database schema (Supabase / Postgres)
 
```mermaid
erDiagram
    TEACHERS ||--o{ SUBJECTS : teaches
    SUBJECTS ||--o{ SUBJECT_STUDENTS : has
    STUDENTS ||--o{ SUBJECT_STUDENTS : enrolls
    SUBJECTS ||--o{ ATTENDANCE_LOGS : has
    STUDENTS ||--o{ ATTENDANCE_LOGS : has
 
    TEACHERS {
        int teacher_id PK
        string username
        string password
        string name
    }
    STUDENTS {
        int student_id PK
        string name
        jsonb face_embedding
        jsonb voice_embedding
    }
    SUBJECTS {
        int subject_id PK
        string subject_code
        string name
        string section
        int teacher_id FK
    }
    SUBJECT_STUDENTS {
        int student_id FK
        int subject_id FK
    }
    ATTENDANCE_LOGS {
        int student_id FK
        int subject_id FK
        timestamp timestamp
        bool is_present
    }
```
 
`subject_students` is the enrollment join table between students and subjects; `attendance_logs` gets one row per student per attendance session (a session is identified by its `timestamp`).
 
## Tech stack
 
| Layer | Technology |
|---|---|
| UI / app framework | [Streamlit](https://streamlit.io) |
| Face detection & embeddings | dlib (`dlib-bin`), `face_recognition_models` |
| Face classification | scikit-learn (linear SVM) |
| Voice embeddings | Resemblyzer (`VoiceEncoder`) |
| Audio loading / segmentation | librosa |
| Database & auth storage | Supabase (Postgres) |
| Password hashing | bcrypt |
| QR code generation | segno |
| Data handling | pandas, numpy |
| Images | Pillow |
 
## Project structure
 
```
SmartPresence/
├── app.py                     # Entry point; routes between home/teacher/student screens
├── requirements.txt
└── src/
    └── screens/
        ├── home_screen.py      # Portal chooser
        ├── teacher_screen.py   # Teacher login/register + dashboard (3 tabs)
        ├── student_screen.py   # Student face-ID login/register + dashboard
        ├── components/
        │   ├── header.py
        │   ├── footer.py
        │   ├── subject_card.py
        │   ├── dialog_create_subject.py
        │   ├── dialog_enroll.py
        │   ├── dialog_auto_enroll.py       # Handles ?join_code= deep links
        │   ├── dialog_add_photos.py
        │   ├── dialog_share_subject.py     # QR code + join link
        │   ├── dialog_voice_attendance.py
        │   └── dialog_attendance_results.py
        ├── database/
        │   ├── config.py       # Supabase client
        │   └── db.py           # All CRUD/query functions
        ├── pipelines/
        │   ├── face_pipeline.py    # dlib + SVM
        │   └── voice_pipeline.py   # Resemblyzer + librosa
        └── ui/
            └── base_layout.py  # Shared CSS styling
```
 
## Getting started
 
### Prerequisites
- Python 3.10–3.12 (the project was developed against 3.12)
- A [Supabase](https://supabase.com) project (free tier works)
- A webcam and microphone for face/voice capture in the browser
### Installation
 
```bash
git clone https://github.com/Divyesh-1729/SmartPresence.git
cd SmartPresence
 
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
 
pip install -r requirements.txt
```
 
`dlib-bin` installs a prebuilt dlib wheel (no local compiler needed), and `face_recognition_models` is pulled directly from GitHub via the `git+https://...` line in `requirements.txt`.
 
### Configure Supabase
 
Create `.streamlit/secrets.toml` in the project root (this path is already git-ignored):
 
```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-SUPABASE-KEY"
```
 
Then create the five tables shown in the [schema](#database-schema-supabase--postgres) above in your Supabase project (Table Editor or SQL editor), matching the column names listed.
 
### Run the app
 
```bash
streamlit run app.py
```

## Credits
 
Built by **Divyesh Puranik** ([@Divyesh-1729](https://github.com/Divyesh-1729)).
