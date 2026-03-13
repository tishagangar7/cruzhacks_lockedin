# LockedIn

LockedIn is a Tinder-style study-group matching app where students can sign up, add profile preferences, upload schedules/syllabi, and browse best-fit study groups.

## Stack

- Backend: Flask + SQLAlchemy + SQLite
- Frontend: Static HTML/CSS/JS

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 backend/app.py
```

Open `http://127.0.0.1:5000`.

## Environment variables

- `FLASK_SECRET_KEY`: strong random secret for sessions.
- `DATABASE_URL`: optional SQLAlchemy connection string.
- `PORT`: HTTP port (default `5000`).
- `SESSION_COOKIE_SECURE`: set to `true` behind HTTPS.
- `SESSION_COOKIE_SAMESITE`: cookie policy (default `Lax`).
- `SESSION_LIFETIME_DAYS`: remember-me session length in days (default `30`).

## Deployment notes

- App serves frontend files from `frontend/` directly.
- Use a production WSGI server (for example `gunicorn`) instead of Flask dev server:

```bash
gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} backend.app:app
```

- Ensure `FLASK_SECRET_KEY` is set in production.
- This repo includes `render.yaml` for one-click Render deployment.
- SQLite is file-based; use a persistent disk or migrate to managed Postgres for production durability.

## Deploy to Render (quick)

1. Push your repo to GitHub.
2. In Render, create a new **Blueprint** and point it to this repo.
3. Render reads `render.yaml` and creates the web service automatically.
4. After first deploy, open `https://<your-service>.onrender.com/health` to confirm status `ok`.