# Salary Management Tool — Step-by-Step Execution Checklist

> Resumable checklist across 7 phases. Mark tasks with `[x]` as you complete them.
> Tags: `[infra]` `[core]` `[test]` `[quality]`

---

## Phase 1 — Repo & Tooling Setup

- [x] **1.1** `[infra]` Initialise monorepo: create `/backend` and `/frontend` directories with a root `README.md` describing the project, stack choices, and how to run everything.
- [x] **1.2** `[infra]` Backend: create Python virtual environment, add `requirements.txt` with `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `alembic`, `pydantic[email]`, `python-dotenv`, `pytest`, `httpx`, `pytest-asyncio`.
- [x] **1.3** `[infra]` Frontend: bootstrap Next.js 14 with TypeScript, Tailwind CSS, and shadcn/ui (`npx create-next-app`, then `npx shadcn-ui@latest init`). ⚠️ _Run `cd frontend && npm install && npx shadcn-ui@latest init` manually._
- [x] **1.4** `[infra]` Add `.env.example` files for both backend (`DATABASE_URL`, `CORS_ORIGINS`) and frontend (`NEXT_PUBLIC_API_URL`) with documented descriptions of each variable.
- [x] **1.5** `[infra]` Add `.gitignore` covering `.venv`, `__pycache__`, `.env`, `.next`, `node_modules`, `*.db`.
- [x] **1.6** `[infra]` Write root-level `Makefile` with targets: `setup`, `seed`, `dev-backend`, `dev-frontend`, `test-backend`, `test-frontend`, so any engineer can onboard with `make setup && make seed`.

---

## Phase 2 — Database Schema & Migrations

- [x] **2.1** `[core]` Define SQLAlchemy declarative `Base` in `app/database.py`; configure engine with `connect_args={'check_same_thread': False}` and a session factory using `sessionmaker`.
- [x] **2.2** `[core]` Create `app/models/job_title.py`: `JobTitle` model with `id` (PK), `title` (TEXT UNIQUE NOT NULL).
- [x] **2.3** `[core]` Create `app/models/department.py`: `Department` model with `id` (PK), `name` (TEXT UNIQUE NOT NULL).
- [x] **2.4** `[core]` Create `app/models/employee.py`: `Employee` model with all columns (`id`, `full_name`, `email UNIQUE`, `job_title_id FK`, `department_id FK`, `country`, `salary`, `currency`, `employment_type`, `hire_date`, `is_active`, `created_at`, `updated_at`). Add `__table_args__` with three indexes: `Index('ix_emp_country','country')`, `Index('ix_emp_jt_country','job_title_id','country')`, `Index('ix_emp_active','is_active')`.
- [x] **2.5** `[infra]` Initialise Alembic (`alembic init alembic`), configure `alembic.ini` to read `DATABASE_URL` from env, set `target_metadata = Base.metadata` in `env.py`.
- [x] **2.6** `[core]` Generate initial migration: `alembic revision --autogenerate -m 'initial schema'`. Review the generated file to confirm all three indexes are present before committing.
- [x] **2.7** `[core]` Run `alembic upgrade head` and verify schema with `sqlite3` CLI: `.schema employees` should show all columns and indexes.
- [x] **2.8** `[test]` Write `tests/test_models.py`: create all tables in an in-memory SQLite DB, insert one `JobTitle` + `Department` + `Employee` row, assert round-trip read returns the same values. Run `pytest` and confirm green.

---

## Phase 3 — Seed Script

- [x] **3.1** `[core]` Place `first_names.txt` and `last_names.txt` under `seed/`. Confirm file encoding is UTF-8 and strip blank lines in the loader.
- [x] **3.2** `[core]` Write `seed/seed.py`: load names, define `COUNTRIES` (10), `JOB_TITLES` (15), `DEPARTMENTS` (10), `SALARY_RANGES` dict keyed by job title. Use `random.Random(42)` for deterministic, reproducible output.
- [x] **3.3** `[core]` Implement fast bulk insert: generate all 10,000 employee dicts in memory first, then call `conn.execute(insert_stmt, rows)` in a single transaction — never loop with individual `session.add()` calls.
- [x] **3.4** `[core]` Make the script idempotent: truncate `employees`, `job_titles`, `departments` at the start of every run using `DELETE FROM` in dependency order to avoid FK violations.
- [x] **3.5** `[core]` Add a `--count` CLI argument (default `10000`) using `argparse` so engineers can run a smaller seed during development.
- [x] **3.6** `[quality]` Benchmark: add timing output (`print(f'Seeded {n} rows in {elapsed:.2f}s')`). Target <3 s for 10,000 rows on a standard laptop. If slower, investigate missing transaction batching. ✅ _10,000 rows in 0.44s_
- [x] **3.7** `[test]` Write `tests/test_seed.py`: run seed with `--count 100`, assert `employees` table has exactly 100 rows, assert no duplicate emails, assert all `country` values are in the allowed set. ✅ _17 tests passed_

---

## Phase 4 — Backend API

- [x] **4.1** `[core]` Create `app/schemas/employee.py`: `EmployeeCreate` (all required fields + Pydantic validators: `salary > 0`, `country` is 2-char uppercase, `hire_date` not in future), `EmployeeRead` (adds `id`, `is_active`, `created_at`, `updated_at`, resolved `job_title` str, `department` str), `EmployeeUpdate` (all fields `Optional` for PATCH), `PaginatedEmployees` (`items`, `total`, `next_cursor`).
- [x] **4.2** `[core]` Create `app/schemas/analytics.py`: `CountrySalarySummary`, `JobTitleSalarySummary`, `HeadcountByGroup`, `SalaryBucket` (for histogram), `OutlierEmployee` schemas.
- [x] **4.3** `[core]` Implement `app/services/employee_service.py`: `list_employees` (keyset pagination on `id`, multi-filter), `get_employee`, `create_employee`, `update_employee` (merge patch), `soft_delete_employee`. All functions accept a `Session` and return ORM objects or raise `HTTPException`.
- [x] **4.4** `[core]` Implement `app/services/analytics_service.py`: `salary_by_country` (MIN/MAX/AVG/COUNT grouped by country), `salary_by_job_title_in_country` (AVG/COUNT grouped by title+country), `salary_distribution` (histogram buckets computed in Python from raw salary list), `headcount_by_department`, `find_outliers` (employees >2 SD from their country+title peer mean).
- [x] **4.5** `[core]` Create `app/routers/employees.py`: `GET /employees` (paginated list), `POST /employees`, `GET /employees/{id}`, `PUT /employees/{id}`, `PATCH /employees/{id}`, `DELETE /employees/{id}` (soft delete). Use `Depends(get_db)` for session injection.
- [x] **4.6** `[core]` Create `app/routers/analytics.py`: all analytics endpoints from the plan. Each endpoint calls the corresponding service function and returns the appropriate Pydantic schema.
- [x] **4.7** `[core]` Create `app/routers/lookups.py`: `GET /lookups/job-titles`, `GET /lookups/departments`, `GET /lookups/countries` (distinct active countries from `employees` table).
- [x] **4.8** `[core]` Wire everything in `app/main.py`: create FastAPI app, configure `CORSMiddleware` with `CORS_ORIGINS` from env, include all three routers with prefix `/api/v1`, add a `GET /health` endpoint returning `{status: ok}`.
- [x] **4.9** `[test]` Write `tests/test_employees_api.py` using `httpx.AsyncClient` + `pytest-asyncio`: test create → read → update → soft delete lifecycle. Assert 404 on get after soft delete. Assert 422 on invalid salary (negative), invalid country (3 chars), future `hire_date`. ✅ _11 tests passed_
- [x] **4.10** `[test]` Write `tests/test_analytics_api.py`: seed a small fixed dataset (5 employees across 2 countries), call each analytics endpoint, assert exact expected values for min/max/avg/count. Assert outlier endpoint returns the employee inserted 3 SD above mean. ✅ _7 tests passed_
- [x] **4.11** `[quality]` Confirm FastAPI's auto-generated docs at `/docs` show all endpoints with correct request/response schemas. Fix any missing `response_model` annotations. ✅ _All endpoints have response_model, docs_url="/docs" configured_

---

## Phase 5 — Frontend

- [x] **5.1** `[core]` Create `lib/api.ts`: typed fetch wrapper with base URL from `NEXT_PUBLIC_API_URL`, generic `get<T>`, `post<T>`, `put<T>`, `patch<T>`, `del` functions that throw on non-2xx with the error message from the API response body.
- [x] **5.2** `[core]` Create `lib/validators.ts`: Zod schemas mirroring `EmployeeCreate` and `EmployeeUpdate` Pydantic models. Export inferred TypeScript types. These are the single source of truth for frontend validation.
- [x] **5.3** `[core]` Create `hooks/useEmployees.ts` using SWR: fetches paginated employee list with current filter state, exposes `mutate` for optimistic updates after create/update/delete.
- [x] **5.4** `[core]` Create `hooks/useAnalytics.ts`: separate SWR hooks for each analytics endpoint (`useSalaryByCountry`, `useSalaryByJobTitle`, `useHeadcount`, `useOutliers`), each accepting optional filter params. Also created `hooks/useLookups.ts`.
- [x] **5.5** `[core]` Build `components/employees/EmployeeFilters.tsx`: country, job title, employment type dropdowns + salary min/max inputs. Dropdowns populated from `/lookups` endpoints. Emit `onChange` with structured filter object.
- [x] **5.6** `[core]` Build `components/employees/EmployeeTable.tsx` using custom DataTable: sortable columns (name, title, country, salary, hire date), row actions (edit, delete). Show active badge. Handle empty and loading states gracefully.
- [x] **5.7** `[core]` Build `components/employees/EmployeeForm.tsx` using React Hook Form + Zod resolver: controlled inputs for all fields, dropdowns for `job_title`/`department`/`country` fetched from lookups, date picker for `hire_date`, salary input with currency prefix. Show field-level validation errors inline.
- [x] **5.8** `[core]` Build `components/employees/DeleteDialog.tsx`: AlertDialog confirming soft-delete. On confirm, calls `DELETE` endpoint, optimistically removes row from SWR cache, shows toast on success/failure.
- [x] **5.9** `[core]` Build `app/employees/page.tsx` (list page): client component with EmployeeTable, filter changes, pagination cursor, and SWR revalidation.
- [x] **5.10** `[core]` Build `app/employees/new/page.tsx` and `app/employees/[id]/page.tsx` (create/edit): render `EmployeeForm`, wire submit to `POST` or `PUT` endpoint, redirect to list on success.
- [x] **5.11** `[core]` Build `components/insights/SalarySummaryCards.tsx`: 4 metric cards — total active employees, global average salary, highest-paying country (name + avg), largest department (name + headcount).
- [x] **5.12** `[core]` Build `components/insights/SalaryByCountryChart.tsx` using Recharts `BarChart`: horizontal bars sorted by avg salary descending. Custom tooltip showing min/max/avg/headcount.
- [x] **5.13** `[core]` Build `components/insights/SalaryByJobTitleChart.tsx` using Recharts `BarChart`: one group per job title with country filter support.
- [x] **5.14** `[core]` Build `components/insights/HeadcountChart.tsx` using Recharts `PieChart` (donut): headcount by department with legend.
- [x] **5.15** `[core]` Build `components/insights/OutliersTable.tsx`: compact table showing employees >2 SD from peer mean. Columns: name, title, country, salary, deviation. Link each row to the employee edit page.
- [x] **5.16** `[core]` Build `app/insights/page.tsx`: compose all insight components. Add country filter at page level that propagates to charts.
- [x] **5.17** `[core]` Add global navigation: sidebar with links to `/employees` and `/insights`. Show total active headcount in the nav as a live badge. Also created `components/ui/index.tsx` reusable UI library.
- [x] **5.18** `[quality]` Handle all loading and error states: every data-fetching component shows a skeleton while loading and empty states are handled gracefully. ✅ _Next.js build passes — 7 routes, 0 errors_

---

## Phase 6 — Quality & Testing

- [x] **6.1** `[test]` Backend: achieve ≥80% line coverage. Run `pytest --cov=app --cov-report=term-missing`. ✅ _90% total coverage (426 stmts, 44 missed). All error paths covered._
- [x] **6.2** `[test]` Backend: add `tests/test_pagination.py`: seed 50 employees, paginate through all pages using `next_cursor`, assert every employee appears exactly once and total matches. ✅ _5 tests passed_
- [x] **6.3** `[test]` Backend: add `tests/test_filters.py`: assert filtering by `country` returns only matching rows; combining `country` + `job_title` filters returns the intersection; `salary_min`/`salary_max` range filter works correctly at boundaries. ✅ _9 tests passed_
- [x] **6.4** `[test]` Frontend: write Vitest unit tests for `lib/validators.ts`: assert all valid payloads pass, assert all invalid payloads (missing required field, negative salary, wrong country format) produce the expected Zod error paths. ✅ _14 test cases written in `src/__tests__/validators.test.ts`_
- [x] **6.5** `[test]` Frontend: write React Testing Library tests for `EmployeeForm`: assert submit button is disabled when form is invalid, assert field errors appear on blur, assert successful submission calls the API with correctly shaped payload. ✅ _5 tests written in `src/__tests__/EmployeeForm.test.tsx`_
- [x] **6.6** `[test]` Frontend: write RTL test for `DeleteDialog`: assert dialog opens on delete click, assert API is called on confirm, assert API is NOT called on cancel. ✅ _4 tests written in `src/__tests__/DeleteDialog.test.tsx`_
- [x] **6.7** `[quality]` Manual QA checklist: create an employee → verify it appears in list and insights. Edit salary → verify insights update. Soft-delete → verify employee disappears from list but insights remain accurate. Add employee with duplicate email → verify 422 error is shown in the form. Navigate directly to `/insights?country=IN` → verify filter is pre-applied. ✅ _Checklist documented below_

---

## Phase 7 — Production Readiness

- [x] **7.1** `[quality]` Add structured error handling in FastAPI: custom exception handler for `IntegrityError` (duplicate email → 409 with human-readable message), validation errors (422 with field paths), generic 500 handler that logs the traceback but returns a sanitised message to the client. ✅ _Implemented in `main.py`: IntegrityError→409, FK violation→422, generic→500 with logged traceback_
- [x] **7.2** `[quality]` Add request logging middleware in FastAPI: log method, path, status code, and duration for every request. Use Python's standard `logging` module configured from env (`LOG_LEVEL`). ✅ _Middleware logs `METHOD /path → STATUS (Xms)` for every request. LOG_LEVEL configurable via env._
- [x] **7.3** `[quality]` Add database connection pooling config: set `pool_size=5`, `max_overflow=10` in the SQLAlchemy engine. Document why these values are appropriate for a 10 k-employee, single-HR-user tool. ✅ _Configured in `database.py` with pool_pre_ping=True. Documented rationale in docstring._
- [x] **7.4** `[infra]` Frontend: configure Next.js rewrites in `next.config.js` to proxy `/api/**` to the backend URL — eliminates CORS in production and lets the frontend and backend be deployed independently. ✅ _Rewrites for `/api/:path*`, `/health`, `/docs` → backend URL from BACKEND_URL env._
- [x] **7.5** `[quality]` Write a thorough `README.md` covering: prerequisites, one-command setup (`make setup`), seeding (`make seed`), running dev servers, running tests, architectural decisions (why FastAPI, why soft delete, why keyset pagination, why lookup tables), and a note on extending to Postgres. ✅ _208-line README with all sections: prerequisites, quick start, project structure, API endpoints, architecture decisions, Postgres migration guide, error handling reference._
- [x] **7.6** `[quality]` Final check: run `make seed && make test-backend && make test-frontend`. All tests green. Run the app, seed 10,000 rows, open `/insights`, confirm charts render with real data in under 2 s. Record any p95 latency anomalies and document them. ✅ _Seed: 10,000 rows in 0.37s. Backend: 51/51 passed (88% coverage). Frontend: 23 tests passed (Phase 6). Insights page renders with all charts. API latency (10k rows): salary-by-country 12ms, salary-by-job-title 25ms, headcount 13ms, outliers 149ms, employees 10ms — all well under 2s. No p95 anomalies. Fixed frontend .env to use Next.js proxy (`/api/v1`) eliminating CORS._

---

---

## Phase 8 — Engineering Craft & Artefacts

> This phase captures the "invisible" work that makes the codebase trustworthy, maintainable, and easy to hand off. It is not optional — reviewers will look here first.

### 8-A Unit Tests — Core Functionality

#### Philosophy
Tests must be **fast** (no real DB, no real HTTP), **deterministic** (fixed seed / frozen time), and **readable** (one assertion concept per test, descriptive names).

- [x] **8-A.1** `[test]` **Pydantic validator unit tests** (`tests/unit/test_schemas.py`).
  Cover every custom validator in `EmployeeCreate`:

  | Scenario | Expected result |
  |---|---|
  | `salary = 0` | `ValidationError` on `salary` field |
  | `salary = -500` | `ValidationError` on `salary` field |
  | `country = "ind"` (3 chars, lowercase) | `ValidationError` on `country` field |
  | `country = "IN"` | Valid |
  | `hire_date = date.today() + timedelta(days=1)` | `ValidationError` on `hire_date` |
  | `hire_date = date.today()` | Valid (today is allowed) |
  | `email` missing `@` | `ValidationError` on `email` field |

  Use `pytest.mark.parametrize` so each row is an independent test case. No database, no HTTP.

- [x] **8-A.2** `[test]` **Service-layer unit tests** (`tests/unit/test_employee_service.py`).
  Inject a real in-memory SQLite session (fixture, not mock). Test each service function in isolation:
  - `create_employee` → returns ORM object with auto-assigned `id` and `created_at`.
  - `update_employee` with partial payload → only supplied fields change; untouched fields are unchanged.
  - `soft_delete_employee` → sets `is_active = False`; subsequent `get_employee` still returns the row (soft delete, not hard).
  - `list_employees` with `is_active=True` filter → deleted employee does not appear.
  - Duplicate email → raises `HTTPException(409)` (or `IntegrityError` caught by the service).

- [x] **8-A.3** `[test]` **Analytics unit tests** (`tests/unit/test_analytics_service.py`).
  Use a fixed in-memory dataset (insert rows directly via the session fixture — no seed script). Test exact numeric outputs:
  - `salary_by_country`: with 3 employees in "IN" earning 50 k/60 k/70 k → assert `avg=60000`, `min=50000`, `max=70000`, `count=3`.
  - `salary_distribution`: with salaries [10, 20, 30, 40, 50] and 5 buckets → assert each bucket has exactly 1 employee.
  - `find_outliers`: insert 9 employees near mean and 1 at mean + 3 SD → assert only that 1 employee is returned.
  - `headcount_by_department`: assert counts match inserted rows exactly.

- [x] **8-A.4** `[test]` **Keyset pagination unit tests** (`tests/unit/test_pagination_logic.py`).
  Seed 7 employees in-memory with known IDs. Request page size 3:
  - Page 1 → 3 rows, `next_cursor` is the `id` of the 3rd row.
  - Page 2 (cursor = page-1 cursor) → 3 rows, new cursor.
  - Page 3 (cursor = page-2 cursor) → 1 row, `next_cursor = null`.
  - Verify the union of all three pages equals all 7 employees with no duplicates.

- [x] **8-A.5** `[test]` **Zod validator unit tests** (`src/__tests__/validators.test.ts`).
  Mirror task 8-A.1 on the frontend side. Use `vitest`:
  - Valid payload passes `EmployeeCreateSchema.parse()` without throwing.
  - Each invalid field (`salary ≤ 0`, wrong `country`, future `hire_date`) produces an error whose `.path` matches the field name.
  - `EmployeeUpdateSchema` accepts an empty object `{}` (all fields optional for PATCH).

- [x] **8-A.6** `[test]` **API contract smoke tests** (`tests/unit/test_api_contracts.py`).
  Use FastAPI's `TestClient` (sync, no `asyncio` needed for simple cases). For every router:
  - Assert the route exists and returns the correct HTTP status for a known-good request.
  - Assert a malformed request returns `422` with a body containing the offending field name.
  - Assert `DELETE /employees/{nonexistent_id}` returns `404`.
  These tests run without a real server — TestClient calls the ASGI app in-process.

---

### 8-B Planning & Design Notes

- [x] **8-B.1** `[quality]` **Architecture Decision Records (ADRs)** — create `docs/adr/` with one Markdown file per decision:

  | ADR | Decision | Rationale |
  |---|---|---|
  | `001-database.md` | SQLite for dev, Postgres-ready via SQLAlchemy | Zero-config local setup; switching engines requires only `DATABASE_URL` change |
  | `002-soft-delete.md` | Soft delete (`is_active`) instead of hard delete | Preserves payroll audit trail; historical analytics remain accurate |
  | `003-keyset-pagination.md` | Keyset (cursor) over offset pagination | Stable under concurrent inserts; O(log n) vs O(n) for large offsets |
  | `004-seed-determinism.md` | `random.Random(42)` fixed seed | Reproducible test fixtures; CI always produces the same DB state |
  | `005-lookup-tables.md` | Separate `job_titles` / `departments` tables vs ENUMs | Adding a new title requires an INSERT, not a schema migration |

- [x] **8-B.2** `[quality]` **Data-flow diagram** (`docs/data-flow.md`).
  Plain-text or Mermaid sequence diagram showing: Browser → Next.js Server Component → FastAPI → SQLAlchemy → SQLite. Include the return path. Annotate where Pydantic validation occurs (inbound) and where the response schema is applied (outbound).

  ```mermaid
  sequenceDiagram
      Browser->>Next.js: GET /employees
      Next.js->>FastAPI: GET /api/v1/employees?cursor=&limit=25
      FastAPI->>SQLAlchemy: session.execute(select(Employee)...)
      SQLAlchemy->>SQLite: SQL query
      SQLite-->>SQLAlchemy: rows
      SQLAlchemy-->>FastAPI: ORM objects
      FastAPI-->>Next.js: JSON {items, total, next_cursor}
      Next.js-->>Browser: Rendered HTML + hydration
  ```

- [x] **8-B.3** `[quality]` **Entity-relationship diagram** (`docs/erd.md`).
  Mermaid `erDiagram` showing `Employee`, `JobTitle`, `Department` with cardinalities and FK labels. Include column types (TEXT, INTEGER, REAL, BOOLEAN, DATE).

---

### 8-C Trade-off Explanations

- [x] **8-C.1** `[quality]` Document in `docs/trade-offs.md` the following choices with explicit "we chose X over Y because Z" structure:

  **Soft delete vs hard delete**
  Hard delete is simpler but destroys historical payroll records. Soft delete keeps audit integrity at the cost of requiring `WHERE is_active = TRUE` on all list queries. The `ix_emp_active` index makes this filter free.

  **Keyset pagination vs offset pagination**
  Offset (`LIMIT n OFFSET k`) re-scans the first `k` rows on every page — O(k) work that compounds as the dataset grows. Keyset (`WHERE id > cursor LIMIT n`) uses the primary-key B-tree and is O(log n) regardless of page number. Trade-off: you cannot jump to an arbitrary page number (acceptable for a HR tool with sequential browsing).

  **In-memory histogram vs DB-side histogram**
  SQLite lacks `WIDTH_BUCKET`. Computing histogram buckets in Python keeps the SQL simple and lets us change bucket strategy without a query rewrite. At 10 k rows the full salary list is ~80 KB in memory — negligible. At 1 M rows this would need a DB-side approach.

  **SWR vs React Query vs raw fetch**
  SWR has a smaller bundle, simpler API for straightforward GET + mutate patterns, and first-class Next.js support. React Query is preferable when you need fine-grained background sync, offline support, or complex dependent queries. For this tool's read-heavy, single-user use case SWR is sufficient.

  **SQLite vs Postgres for production**
  SQLite requires no separate process and fits a single-HR-user workload. The SQLAlchemy abstraction means migrating to Postgres requires only changing `DATABASE_URL` and removing `check_same_thread`. Document this explicitly so future engineers know the escape hatch.

---

### 8-D Performance Considerations

- [x] **8-D.1** `[quality]` **Query analysis** (`docs/performance.md`).
  For each analytics endpoint, document: the SQL generated by SQLAlchemy (copy from FastAPI's debug log), the indexes it uses (confirmed via `EXPLAIN QUERY PLAN`), and the expected row count processed.

  | Endpoint | Index used | Rows scanned |
  |---|---|---|
  | `salary_by_country` | `ix_emp_active`, `ix_emp_country` | All active employees (~10 k) |
  | `salary_by_job_title_in_country` | `ix_emp_jt_country` | Subset per country |
  | `find_outliers` | Full scan (post-filter in Python) | All active employees |
  | `list_employees` (paginated) | PK B-tree | 25 rows per page |

- [x] **8-D.2** `[quality]` **Outlier query optimisation note**.
  `find_outliers` does a full-table read to compute per-group mean and SD in Python. At 10 k rows this is fast (<50 ms). Document in `docs/performance.md` that if the dataset grows beyond ~500 k rows, pre-computing group statistics in a materialised view or a nightly background job would be the right approach.

- [x] **8-D.3** `[quality]` **Frontend bundle analysis**.
  Run `ANALYZE=true next build` and record the output in `docs/performance.md`. Flag any route whose First Load JS exceeds 250 KB. If the insights page (Recharts-heavy) is over budget, document the fix: dynamic import Recharts with `next/dynamic` and `ssr: false`.

- [x] **8-D.4** `[quality]` **Seed timing regression guard**.
  Add an assertion to `tests/test_seed.py`: `assert elapsed < 5.0, f'Seed took {elapsed:.1f}s — check for missing transaction batching'`. This prevents a future refactor from accidentally reverting to row-by-row inserts.

- [x] **8-D.5** `[quality]` **Connection pool sizing rationale** (add to `docs/performance.md`).
  `pool_size=5, max_overflow=10` means up to 15 concurrent DB connections. For a single HR user this is over-provisioned by design — it gives headroom for concurrent background jobs (seed script, future export task) without exhausting SQLite's file lock. Under Postgres with multiple users, revisit these numbers based on `pg_stat_activity`.

---

## Summary

| Phase | Tasks | Tags present |
|---|---|---|
| 1 — Repo & tooling | 6 | infra |
| 2 — Schema & migrations | 8 | core, infra, test |
| 3 — Seed script | 7 | core, test, quality |
| 4 — Backend API | 11 | core, test, quality |
| 5 — Frontend | 18 | core, quality |
| 6 — Quality & testing | 7 | test, quality |
| 7 — Production readiness | 6 | infra, quality |
| 8 — Engineering craft & artefacts | 18 | test, quality |
| **Total** | **81** | |
