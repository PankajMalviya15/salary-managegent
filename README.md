# Salary Management Tool

A full-stack salary management application for HR teams to manage employee records, visualise compensation analytics, and identify salary outliers across departments and countries.

---

## Tech Stack

| Layer      | Technology                                                        |
| ---------- | ----------------------------------------------------------------- |
| **Backend**  | Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2      |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Database** | SQLite (dev) — swappable to PostgreSQL for production              |
| **Testing**  | pytest + httpx (backend), Vitest + React Testing Library (frontend) |

---

## Project Structure

```
salary_management/
├── backend/            # FastAPI application
│   ├── app/            # Application package (models, routers, services, schemas)
│   ├── alembic/        # Database migrations
│   ├── seed/           # Seed data scripts
│   ├── tests/          # Backend test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/           # Next.js 14 application
│   ├── app/            # App Router pages
│   ├── components/     # Reusable UI components
│   ├── hooks/          # Custom React hooks (SWR)
│   ├── lib/            # API client, validators, utilities
│   └── .env.example
├── Makefile            # Developer workflow commands
├── README.md           # ← You are here
└── checklist.md        # Step-by-step execution checklist
```

---

## Quick Start

### Prerequisites

- **Python** ≥ 3.11
- **Node.js** ≥ 18 LTS
- **npm** ≥ 9
- **make** (GNU Make)

### One-Command Setup

```bash
make setup        # Creates venv, installs deps for backend & frontend
make seed         # Seeds the database with 10,000 sample employees
```

### Running Development Servers

```bash
make dev-backend   # Starts FastAPI on http://localhost:8000
make dev-frontend  # Starts Next.js on http://localhost:3000
```

### Running Tests

```bash
make test-backend   # Runs pytest for the backend
make test-frontend  # Runs vitest for the frontend
```

---

## Key Features

- **Employee CRUD** — Create, read, update, and soft-delete employee records with full validation.
- **Keyset Pagination** — Efficient cursor-based pagination for large datasets.
- **Multi-Filter Search** — Filter by country, job title, department, employment type, and salary range.
- **Compensation Analytics** — Average/min/max salary by country and job title, headcount breakdowns, salary distribution histograms.
- **Outlier Detection** — Automatically flags employees whose salary deviates > 2 SD from their peer group mean.
- **Lookup Tables** — Normalised job titles and departments for data consistency.

---

## Environment Variables

See `.env.example` files in `/backend` and `/frontend` for all required configuration.

---

## License

MIT
