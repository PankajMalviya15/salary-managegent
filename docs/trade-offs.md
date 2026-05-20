# Engineering Trade-offs

> Each decision follows the structure: **We chose X over Y because Z.**

---

## 1. Soft Delete vs Hard Delete

**We chose soft delete** (`is_active = FALSE`) **over hard delete** (`DELETE FROM employees`) **because** historical payroll records must be preserved for audit compliance and analytics accuracy.

**What we gain:**
- Past analytics queries ("average salary in Q3 2024") remain reproducible.
- Reactivation of returning contractors requires no data re-entry.
- Future FK-dependent tables (reviews, payroll runs) won't suffer cascade deletes.

**What we pay:**
- Every list query needs `WHERE is_active = TRUE`. Mitigated by the `ix_emp_active` index, which makes this filter a B-tree lookup (essentially free).
- Database grows monotonically. At 10k employees with ~5% annual churn, storage impact is negligible for decades.

---

## 2. Keyset Pagination vs Offset Pagination

**We chose keyset pagination** (`WHERE id > cursor LIMIT n`) **over offset pagination** (`LIMIT n OFFSET k`) **because** offset performance degrades linearly with page depth.

**What we gain:**
- O(log n) page fetch regardless of depth (uses PK B-tree).
- Stable results under concurrent inserts — no skipped/duplicated rows.

**What we pay:**
- Cannot jump to arbitrary page numbers (e.g., "go to page 47"). Users must traverse sequentially. Acceptable for an HR tool where filters narrow results and sequential browsing is the norm.

---

## 3. In-Memory Histogram vs DB-Side Histogram

**We chose in-memory histogram computation** (Python) **over DB-side** (`WIDTH_BUCKET`) **because** SQLite lacks `WIDTH_BUCKET` and computing buckets in Python keeps the SQL simple.

**What we gain:**
- Database-agnostic — works identically on SQLite and Postgres.
- Bucket strategy (equal-width, percentile, logarithmic) can be changed in Python without rewriting SQL.

**What we pay:**
- Loads all salary values into memory (~80 KB for 10k rows — negligible).
- At ~1M rows, this approach would need refactoring to a DB-side solution. Document this as a known scaling threshold.

---

## 4. SWR vs React Query vs Raw Fetch

**We chose SWR** **over React Query and raw fetch** **because** SWR has a smaller bundle, simpler API, and first-class Next.js support.

**What we gain:**
- ~4 KB bundle vs ~12 KB for React Query (TanStack Query v5).
- Simpler mental model: `useSWR(key, fetcher)` + `mutate()` covers all our use cases.
- Built-in stale-while-revalidate pattern gives instant UI with background refresh.

**What we pay:**
- Less control over background sync timing, retry strategies, and cache invalidation granularity.
- No built-in offline support or optimistic mutation rollback (React Query excels here).
- For this tool's read-heavy, single-user use case, these trade-offs are acceptable.

---

## 5. SQLite vs Postgres for Production

**We chose SQLite** **over Postgres for development** **because** it requires no external service and fits the single-HR-user workload.

**What we gain:**
- Zero-config: no Docker, no port conflicts, no credentials.
- `make setup && make seed` gets any engineer productive in under 60 seconds.
- File-portable: the `.db` file can be copied or deleted trivially.

**What we pay:**
- No concurrent write support (WAL mode helps but doesn't match Postgres).
- Missing advanced SQL features (`LATERAL JOIN`, `MATERIALIZED VIEW`, `WIDTH_BUCKET`).
- Not suitable for multi-user production deployment.

**Escape hatch:** The SQLAlchemy ORM abstraction means migrating to Postgres requires:
1. `pip install psycopg2-binary`
2. Change `DATABASE_URL` in `.env`
3. `make migrate && make seed`

The `pool_size=5` and `max_overflow=10` settings in `database.py` are pre-configured for Postgres.
