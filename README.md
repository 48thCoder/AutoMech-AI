# AutoMech AI

An AI-powered automotive diagnostic and booking platform. AutoMech AI guides vehicle owners through interactive problem troubleshooting, symptom collection, multimodal analysis (images, audio, video), diagnosis generation, and mechanic appointment booking.

---

## Features

- **Automotive Symptom Triage**: Categorizes issues across engine, brakes, electrical, tyres, AC, transmission, suspension, and body.
- **Multimodal Inspection**: Accepts images, audio recordings (e.g. engine knocking, brake squeals), and video clips for diagnostics.
- **AI Diagnostics**: Leverages Google Gemini to analyze symptoms and uploaded media to produce structured repair summaries, probable causes, severity classifications, and estimated costs/times.
- **Service Appointment Booking**: Streamlined mechanic booking linked directly to generated diagnostic reports.
- **Interactive Web Interface**: React + Vite frontend dashboard with real-time chat, upload triggers, live diagnostic cards, and booking modals.
- **OpenAPI & Swagger Documentation**: Interactive API documentation powered by `drf-spectacular`.

---

## Tech Stack

- **Frontend**: React, Vite, Lucide Icons, Modern CSS
- **Backend**: Django, Django REST Framework
- **AI / Multimodal**: Google Generative AI (Gemini)
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Database**: SQLite (default development)
- **CORS Handling**: `django-cors-headers`

---

## Project Structure

```text
AutoMech AI/
├── backend/
│   ├── api/
│   │   ├── migrations/
│   │   ├── services/
│   │   │   ├── conversation_service.py
│   │   │   └── gemini_service.py
│   │   ├── tests/
│   │   ├── admin.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── config/
│   ├── .env
│   ├── .env.example
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Getting Started

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   GEMINI_API_KEY=your-gemini-api-key-here
   MAX_UPLOAD_SIZE_MB=25
   MEDIA_ROOT=media/
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the Django server:
   ```bash
   python manage.py runserver
   ```
   Backend runs at `http://127.0.0.1:8000/`.

---

### 2. Frontend Setup

1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Frontend runs at `http://localhost:5173/`.

---

## API Documentation

When the backend server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **Schema JSON**: `http://127.0.0.1:8000/api/schema/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## License

This project is licensed under the MIT License.