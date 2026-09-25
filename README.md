# AutoMech AI

An AI-powered automotive diagnostic and booking platform. AutoMech AI guides vehicle owners through interactive problem troubleshooting, symptom collection, multimodal analysis (images, audio, video), diagnosis generation, and mechanic appointment booking.

---

## Features

- **Automotive Symptom Triage**: Categorizes issues across engine, brakes, electrical, tyres, AC, transmission, suspension, and body.
- **Multimodal Inspection**: Accepts images, audio recordings (e.g. engine knocking, brake squeals), and video clips for diagnostics.
- **AI Diagnostics**: Leverages Google Gemini to analyze symptoms and uploaded media to produce structured repair summaries, probable causes, severity classifications, and estimated costs/times.
- **Service Appointment Booking**: Streamlined mechanic booking linked directly to generated diagnostic reports.
- **OpenAPI & Swagger Documentation**: Interactive API documentation powered by `drf-spectacular`.

---

## Tech Stack

- **Backend**: Django, Django REST Framework
- **AI / Multimodal**: Google Generative AI (Gemini)
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Database**: SQLite (default development)
- **CORS Handling**: `django-cors-headers`

---

## Project Structure

```text
AutoMech AI/
└── backend/
    ├── api/
    │   ├── migrations/
    │   ├── services/
    │   ├── tests/
    │   ├── admin.py
    │   ├── exceptions.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── urls.py
    │   └── views.py
    ├── config/
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── .env
    ├── .env.example
    ├── manage.py
    └── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Gemini API key

### Installation

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

4. Configure environment variables:
   Copy `.env.example` to `.env` and fill in your values:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   GEMINI_API_KEY=your-gemini-api-key-here
   MAX_UPLOAD_SIZE_MB=25
   MEDIA_ROOT=media/
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend server will run at `http://127.0.0.1:8000/`.

---

## API Documentation

When the development server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **Schema JSON**: `http://127.0.0.1:8000/api/schema/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## License

This project is licensed under the MIT License.