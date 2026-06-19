# FastAPI Blog

A full-stack blog application built with FastAPI, SQLAlchemy (async), Jinja2 templates, and JWT auth.

## Features

- User registration & login (JWT)
- Create, edit, delete posts
- Like posts
- User profile pages
- Profile picture upload (AWS S3)
- Password reset via email
- Change password
- Delete account
- Pagination / load more
- Clean black-and-white UI

## Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy** (async) + **Alembic** migrations
- **SQLite** (dev) / **PostgreSQL** (prod)
- **AWS S3** for profile pictures
- **JWT** (PyJWT) + **pwdlib[argon2]** for auth
- **uv** for dependency management

---

## Quick Start (local dev with SQLite)

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and set up

```bash
cd fastapi-blog
cp .env.example .env
```

Edit `.env` — at minimum set:

```env
DATABASE_URL=sqlite+aiosqlite:///./blog.db
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
S3_BUCKET_NAME=local-bucket   # ignored unless you upload images
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run fastapi dev main.py
```

Visit **http://localhost:8000** — that's it.

---

## Production (PostgreSQL + Docker)

### 1. Set env vars

```env
DATABASE_URL=postgresql+psycopg://user:pass@db/blogdb
SECRET_KEY=<strong-random-secret>
S3_BUCKET_NAME=your-real-bucket
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=<sendgrid-api-key>
MAIL_FROM=noreply@yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

### 2. Build and run

```bash
docker build -t fastapi-blog .
docker run -p 8000:8000 --env-file .env fastapi-blog
```

Run migrations before starting:

```bash
docker run --env-file .env fastapi-blog uv run alembic upgrade head
```

---

## uv commands cheatsheet

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Add a package | `uv add <package>` |
| Add dev dep | `uv add --dev <package>` |
| Run app (dev) | `uv run fastapi dev main.py` |
| Run app (prod) | `uv run fastapi run main.py` |
| Run migrations | `uv run alembic upgrade head` |
| Generate migration | `uv run alembic revision --autogenerate -m "description"` |
| Run tests | `uv run pytest` |

---

## API Docs

Available at `/docs` (Swagger UI) or `/redoc`.
