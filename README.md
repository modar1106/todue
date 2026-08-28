# Todue  Clone — Full-Stack Todo List Web App

A modern, Todue -inspired Todo List application with multi-user authentication, built with **FastAPI** (Python), **Vue 3 + Vite**, and **Supabase** (PostgreSQL).

## Features

- 🔐 **Multi-User Auth** — Register/Login with Supabase Auth + JWT
- 📝 **CRUD Operations** — Create, Read, Update, Delete todos
- 🔍 **Filtering** — Filter by status, priority, and keyword search
- ↕️ **Sorting** — Sort by date, title, priority, status (asc/desc)
- 📄 **Pagination** — Offset-based with configurable page sizes
- ⚡ **Bulk Insert** — Generate 1,000 random todos for testing
- 🆔 **UUID v7** — Time-ordered unique IDs for every todo
- 🔒 **Row Level Security** — Each user only sees their own data
- 🎨 **Todue -Inspired UI** — Dark theme, clean layout, micro-animations

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Axios |
| Backend | FastAPI, Pydantic, Uvicorn |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth, JWT (python-jose) |
| Data Gen | Faker, UUID7 |

## Project Structure

```
todoweb-ebm/
├── backend/          # FastAPI REST API
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── config.py       # Environment config
│   │   ├── database.py     # Supabase client
│   │   ├── models.py       # Pydantic schemas
│   │   ├── security.py     # JWT auth
│   │   ├── routes/         # API endpoints
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/         # Vue 3 + Vite
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── composables/    # Reactive state
│   │   └── utils/          # API client
│   └── package.json
└── database/         # SQL migration
    └── migration.sql
```

## Quick Start with Docker (Recommended 🐳)

Make sure you have [Docker](https://www.docker.com/) and Docker Compose installed.

1. Ensure your Supabase credentials are set in `backend/.env`:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   JWT_SECRET=your-jwt-secret
   ```

2. Run the entire application with one command:
   ```bash
   docker compose up --build
   ```

- **Frontend (Todue)**: [http://localhost:5173](http://localhost:5173) or [http://localhost](http://localhost)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Manual Local Setup (Without Docker)

### 1. Setup Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Run `database/migration.sql` in the SQL Editor
3. Go to **Settings → API** and copy your credentials

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Copy and fill in credentials
copy .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/todos` | List todos (filter/sort/paginate) |
| GET | `/api/todos/{id}` | Get single todo |
| POST | `/api/todos` | Create todo |
| PUT | `/api/todos/{id}` | Update todo |
| DELETE | `/api/todos/{id}` | Delete todo |
| POST | `/api/todos/generate-bulk` | Generate 1,000 random todos |

### Query Parameters (GET /api/todos)

| Param | Type | Example | Description |
|---|---|---|---|
| `status` | enum | `pending` | Filter: pending, progress, done |
| `priority` | enum | `high` | Filter: low, medium, high |
| `search` | string | `report` | Search title/description |
| `sort_by` | enum | `created_at` | Sort field |
| `sort_order` | enum | `desc` | asc or desc |
| `page` | int | `1` | Page number |
| `page_size` | int | `10` | Items per page (max 100) |
