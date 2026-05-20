# 💰 Salary Management Tool

A full-stack application for managing 10,000+ employee records and analysing compensation data with interactive charts and outlier detection.

**Backend**: Python · FastAPI · SQLAlchemy · SQLite  
**Frontend**: Next.js 14 · React 18 · Recharts · SWR · Zod  
**Testing**: pytest (90% coverage) · Vitest · React Testing Library

---

## 📋 Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| make | any |

---

## 🚀 Quick Start

```bash
# 1. One-command setup (creates venv, installs all deps)
make setup

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Seed the database with 10,000 employees
make seed

# 4. Start both dev servers (in separate terminals)
make dev-backend    # → http://localhost:8000
make dev-frontend   # → http://localhost:3000
```

The app is now running:
- **Dashboard**: http://localhost:3000/employees
- **Insights**: http://localhost:3000/insights
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
salary_managegent/
├── Makefile                  # Developer task runner
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app (CORS, error handlers, logging)
│   │   ├── database.py       # SQLAlchemy engine + connection pooling
│   │   ├── models/           # ORM models (Employee, JobTitle, Department)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic (CRUD, analytics)
│   │   └── routers/          # API endpoints (/employees, /analytics, /lookups)
│   ├── alembic/              # Database migrations
│   ├── seed/                 # Faker-based data seeder
│   ├── tests/                # pytest test suite (51 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (/employees, /insights)
│   │   ├── components/       # UI components (employees, insights, sidebar)
│   │   ├── hooks/            # SWR data hooks
│   │   └── lib/              # API client, Zod validators
│   └── package.json
└── checklist.md              # Implementation progress tracker
```

---

## 🧪 Running Tests

```bash
# Backend (pytest, 51 tests, 90% coverage)
make test-backend

# Frontend (Vitest, validators + RTL component tests)
make test-frontend

# Both
make seed && make test-backend && make test-frontend
```

---

## 🌱 Seeding

```bash
# Default: 10,000 employees
make seed

# Custom count for development
make seed-small          # 100 rows
cd backend && .venv/bin/python -m seed.seed --count 500   # any count
```

The seeder is **idempotent** — it truncates tables before inserting. It generates:
- 15 job titles, 8 departments (lookup tables)
- N employees with realistic names, emails, salaries, and hire dates
- 10 countries, 3 employment types, 3 currencies

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api/v1`.

### Employees
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/employees` | Paginated list with filters |
| `POST` | `/employees` | Create employee |
| `GET` | `/employees/{id}` | Get by ID |
| `PUT` | `/employees/{id}` | Full update |
| `PATCH` | `/employees/{id}` | Partial update |
| `DELETE` | `/employees/{id}` | Soft-delete |

**Filters**: `country`, `job_title_id`, `department_id`, `employment_type`, `salary_min`, `salary_max`, `is_active`  
**Pagination**: `?cursor=<id>&limit=20` (keyset pagination)

### Analytics
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/analytics/salary-by-country` | Min/max/avg/count per country |
| `GET` | `/analytics/salary-by-job-title` | Avg/count per title (optional `?country=`) |
| `GET` | `/analytics/salary-distribution` | Histogram buckets (`?buckets=10`) |
| `GET` | `/analytics/headcount` | Headcount by department |
| `GET` | `/analytics/outliers` | Employees >2σ from peer mean |

### Lookups
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/lookups/job-titles` | All job titles |
| `GET` | `/lookups/departments` | All departments |
| `GET` | `/lookups/countries` | Distinct active countries |

---

## 🏛️ Architectural Decisions

### Why FastAPI?
- **Type safety**: Pydantic schemas auto-validate requests and generate OpenAPI docs.
- **Performance**: async-capable with low overhead — handles 10k employee datasets comfortably.
- **Developer experience**: auto-generated `/docs` page for instant API exploration.

### Why Soft Delete?
Employees are deactivated (`is_active = False`) rather than removed. This:
- Preserves audit trails and historical analytics accuracy.
- Allows reactivation without data re-entry.
- Prevents FK cascade issues with future feature tables (reviews, payroll).

### Why Keyset Pagination?
- **O(1) performance** regardless of page depth (vs. OFFSET which is O(n)).
- Consistent results when data is inserted between page fetches.
- Simple cursor-based API: `?cursor=<last_id>&limit=20`.

### Why Lookup Tables?
`job_titles` and `departments` are separate tables rather than free-text columns:
- Enforces data consistency via foreign keys.
- Enables efficient aggregation queries (GROUP BY integer FK is faster).
- Allows renaming a title/department in one place.
- Powers dropdown menus in the frontend via `/lookups` endpoints.

### Why SQLite (and how to switch to Postgres)?
SQLite was chosen for zero-config development — no database server needed. To switch:

1. Install the Postgres driver: `pip install psycopg2-binary`
2. Update `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/salary_management
   ```
3. Run migrations: `make migrate`
4. Re-seed: `make seed`

The `pool_size=5` and `max_overflow=10` settings in `database.py` will then take effect.

---

## 🛡️ Error Handling

| Status | When | Message |
|--------|------|---------|
| `409` | Duplicate email | "An employee with this email address already exists." |
| `422` | Invalid FK / validation | Pydantic error details or "Referenced job title or department does not exist." |
| `404` | Employee not found | "Employee not found." |
| `500` | Unexpected error | "An internal server error occurred." (traceback logged server-side) |

---

## 📊 Frontend Features

- **Employee Management**: Create, edit, filter, paginate, and soft-delete employees.
- **Compensation Insights**: 4 summary cards, salary-by-country bar chart, salary-by-job-title chart, headcount donut chart, outlier detection table.
- **Dark Theme**: Glassmorphism design with Inter font, gradient accents, and micro-animations.
- **Loading States**: Skeleton loaders on every data-fetching component.
- **Validation**: Zod schemas mirror backend Pydantic models for instant client-side feedback.

---

## 📝 License

Private project — not licensed for redistribution.
