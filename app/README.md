# TaskFlow — Full-Stack Task Manager

A production-ready task management API built with **Clean Architecture**, FastAPI, SQLAlchemy 2.0 (async), and JWT authentication. Includes a premium single-page frontend with no build tools required.

---

## Architecture

```
project/
├── domain/            # Entities + abstract repository interfaces
├── application/       # Use cases, DTOs, validators
├── infrastructure/    # SQLAlchemy repos, JWT, password hashing
├── presentation/      # FastAPI routers, DI wiring, static frontend
└── tests/             # Unit + integration tests
```

Each layer depends only inward — `presentation → application → domain`. Infrastructure implements domain interfaces.

---

## Quick Start (Development)

### 1. Prerequisites
- Python 3.11+
- (Optional) virtualenv / conda

### 2. Install dependencies
```bash
cd app
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` and set a strong `SECRET_KEY` (min 32 characters).

### 4. Run the server
```bash
uvicorn main:app --reload
```

Open: **http://localhost:8000** — the SPA frontend loads automatically.

Swagger UI: **http://localhost:8000/docs**

---

## Running Tests

```bash
pytest -v
```

To see coverage:
```bash
pip install pytest-cov
pytest --cov=. --cov-report=term-missing -v
```

---

## Docker (Production)

Uses PostgreSQL instead of SQLite. Add `asyncpg` to requirements for PostgreSQL support:
```bash
pip install asyncpg
```

```bash
docker-compose up --build
```

API available at **http://localhost:8000**.

---

## API Reference

### Authentication — `/api/v1/auth`

| Method | Endpoint   | Description               | Auth Required |
|--------|------------|---------------------------|---------------|
| POST   | /register  | Register a new user        | No            |
| POST   | /login     | Login, receive JWT tokens  | No            |
| POST   | /refresh   | Refresh access token       | No            |

### Tasks — `/api/v1/tasks`

| Method | Endpoint       | Description                      | Auth Required |
|--------|----------------|----------------------------------|---------------|
| POST   | /              | Create task                      | Yes           |
| GET    | /              | List tasks (filterable, paginated)| Yes          |
| GET    | /{id}          | Get one task                     | Yes           |
| PUT    | /{id}          | Update task                      | Yes           |
| DELETE | /{id}          | Soft-delete task                 | Yes           |

**Query parameters for GET /tasks:**
- `status`: `pending` | `in_progress` | `done`
- `limit`: integer, default `20`, max `100`
- `offset`: integer, default `0`

---

## Security Design
- Passwords hashed with bcrypt (cost factor 12)
- JWT: short-lived access tokens (30 min) + long-lived refresh tokens (7 days)
- Token type field prevents access tokens from being used as refresh tokens
- All private routes validate Bearer token on every request
- Soft deletion preserves data integrity
- Users can only access their own tasks — enforced at repository level

---

## Frontend Features
- Auth toggle (Login / Register) with inline validation
- Dashboard with live stats (total, pending, in-progress, done)
- Task board with status filter pills and pagination
- Create/Edit modal (no page reload)
- Toast notifications for all user actions
- Skeleton loaders during fetch
- Token stored in JavaScript memory only (not localStorage)
- Fully responsive (mobile + desktop)
