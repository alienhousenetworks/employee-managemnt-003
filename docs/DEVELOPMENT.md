# Development guide

## Prerequisites
- Python 3.12+
- Node.js 22+
- Flutter stable SDK
- PostgreSQL 16+
- Redis 7+

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## AI service
```bash
cd ai_services
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8001
```

## Web
```bash
cd web
npm ci
npm run dev
```

## Mobile
```bash
cd mobile
flutter pub get
flutter run
```

## Configuration
Copy example environment files and replace development-only values. Never commit real credentials. Production requires HTTPS, managed secrets, database backups, restricted CORS, rate limits and tested restoration.

## Verification
Run backend pytest, frontend lint/typecheck/tests, FastAPI tests and Flutter analyze/tests before merging. Integration tests requiring live provider credentials must be clearly marked and must not be represented as passing when skipped.
