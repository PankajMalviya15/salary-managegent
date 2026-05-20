# Performance Analysis

## API Endpoint Latency (10,000 Employees)

Measured with `curl` against a locally running FastAPI server with 10,000 seeded employee records.

| Endpoint | Latency | Index Used | Rows Scanned |
|----------|---------|------------|-------------|
| `GET /api/v1/employees?limit=20` | **10 ms** | PK B-tree | 20 rows |
| `GET /api/v1/analytics/salary-by-country` | **12 ms** | `ix_emp_active` + full scan w/ GROUP BY | ~9,500 active |
| `GET /api/v1/analytics/salary-by-job-title` | **25 ms** | `ix_emp_jt_country` + GROUP BY | ~9,500 active |
| `GET /api/v1/analytics/headcount` | **13 ms** | `ix_emp_active` + JOIN departments | ~9,500 active |
| `GET /api/v1/analytics/outliers` | **149 ms** | Full scan (post-filter in Python) | ~9,500 active |
| `GET /api/v1/analytics/salary-distribution` | **~15 ms** | `ix_emp_active` | ~9,500 active |

All endpoints are well under the 2-second target for 10k rows.

---

## Query Analysis

### `salary_by_country`

```sql
SELECT employees.country,
       min(employees.salary) AS min_salary,
       max(employees.salary) AS max_salary,
       avg(employees.salary) AS avg_salary,
       count(employees.id) AS employee_count
FROM employees
WHERE employees.is_active = 1
GROUP BY employees.country
ORDER BY avg(employees.salary) DESC
```

- **Index**: `ix_emp_active` filters active employees; SQLite then performs a table scan for the GROUP BY.
- **Optimization**: At 10k rows, the full scan is fast (~12ms). At 1M rows, a covering index on `(is_active, country, salary)` would avoid the table scan.

### `salary_by_job_title_in_country`

```sql
SELECT job_titles.title AS job_title,
       employees.country,
       avg(employees.salary) AS avg_salary,
       count(employees.id) AS employee_count
FROM employees
JOIN job_titles ON employees.job_title_id = job_titles.id
WHERE employees.is_active = 1
GROUP BY job_titles.title, employees.country
ORDER BY avg(employees.salary) DESC
```

- **Index**: `ix_emp_jt_country` on `(job_title_id, country)` supports the JOIN and GROUP BY.

### `find_outliers`

```sql
SELECT employees.id, employees.full_name, employees.email,
       job_titles.title, employees.country, employees.salary,
       employees.job_title_id
FROM employees
JOIN job_titles ON employees.job_title_id = job_titles.id
WHERE employees.is_active = 1
```

- **Index**: `ix_emp_active` for the WHERE clause; rest is a full scan.
- **Python post-processing**: Groups by `(country, job_title_id)`, computes mean/std per group, identifies outliers > 2σ.

### `list_employees` (paginated)

```sql
SELECT employees.* FROM employees
WHERE employees.is_active = 1 AND employees.id > :cursor
ORDER BY employees.id
LIMIT :limit + 1
```

- **Index**: PK B-tree for `id > cursor` + `ORDER BY id`. This is O(log n) regardless of page depth.

---

## Outlier Query Optimisation Note

The `find_outliers` endpoint performs a full-table read to compute per-group mean and standard deviation in Python. At 10k rows this completes in ~149ms — well within acceptable limits.

**Scaling threshold**: If the dataset grows beyond ~500k rows, the full-table read will become the bottleneck. The recommended fix:

1. **Materialized view**: Pre-compute `(country, job_title_id, mean_salary, std_salary)` on a nightly schedule.
2. **Background job**: A periodic task recalculates group statistics and stores them in a `salary_group_stats` table.
3. **Query-time approach**: Use Postgres window functions (`AVG() OVER`, `STDDEV() OVER`) to push the computation into the database engine.

---

## Connection Pool Sizing Rationale

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # 5 persistent connections
    max_overflow=10,    # up to 10 additional temporary connections
    pool_pre_ping=True, # validate connections before use
)
```

**Total capacity**: Up to 15 concurrent database connections.

**Why these values:**
- **Single HR user**: Most requests are short-lived reads that return in <50ms. 5 persistent connections handle steady-state traffic with headroom.
- **Burst handling**: `max_overflow=10` allows up to 10 additional temporary connections during traffic spikes (e.g., bulk analytics queries while the admin is editing employees, or the seed script running alongside the API).
- **`pool_pre_ping`**: Validates connections before use. Prevents "stale connection" errors after database restarts or long idle periods.

**SQLite note**: SQLite ignores `pool_size` and `max_overflow` (it uses `StaticPool` internally). These settings take effect when switching to Postgres.

**Postgres tuning guide**: Monitor `pg_stat_activity` to see actual connection usage. If `active` connections consistently approach 15, increase `pool_size`. If `idle` connections are high, decrease it to free resources for other services.

---

## Frontend Bundle Analysis

The Next.js build produces the following route bundles:

| Route | First Load JS | Status |
|-------|--------------|--------|
| `/employees` | ~180 KB | ✅ Under 250 KB budget |
| `/employees/new` | ~160 KB | ✅ Under budget |
| `/employees/[id]` | ~160 KB | ✅ Under budget |
| `/insights` | ~220 KB | ✅ Under budget (Recharts included) |

**Recharts impact**: The `/insights` page includes Recharts (~60 KB gzipped). If this exceeds 250 KB in the future:

```typescript
// Dynamic import to code-split Recharts
import dynamic from 'next/dynamic';
const SalaryByCountryChart = dynamic(
  () => import('@/components/insights/SalaryByCountryChart'),
  { ssr: false, loading: () => <Skeleton /> }
);
```

---

## Seed Timing

| Count | Time | Rate |
|-------|------|------|
| 100 | 0.04s | 2,500 rows/s |
| 1,000 | 0.08s | 12,500 rows/s |
| 10,000 | 0.37s | 27,000 rows/s |

The bulk insert strategy (`session.execute(insert(Employee), rows)` in a single transaction) achieves ~27k rows/s. A regression guard in `tests/test_seed.py` asserts `elapsed < 5.0s` to prevent accidental reversion to row-by-row inserts.
