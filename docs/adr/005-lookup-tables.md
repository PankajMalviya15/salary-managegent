# ADR-005: Separate Lookup Tables for Job Titles and Departments

**Status:** Accepted  
**Date:** 2024-01-15  
**Decision:** Store job titles and departments in separate normalized tables (`job_titles`, `departments`) rather than as free-text columns or ENUMs.

## Context

Employees have a job title and department. These could be stored as free-text strings on the employee row, as database ENUMs, or as separate lookup tables with foreign keys.

## Decision

We chose **separate lookup tables** with foreign key relationships.

## Rationale

- **Data consistency**: Foreign keys prevent typos like "Sofware Engineer" vs "Software Engineer". The database enforces referential integrity.
- **Efficient aggregation**: `GROUP BY job_title_id` (integer FK) is faster than `GROUP BY job_title` (variable-length string). The composite index `ix_emp_jt_country` on `(job_title_id, country)` powers the analytics queries.
- **Single-point rename**: Renaming "Data Analyst" to "Analytics Engineer" is a single `UPDATE job_titles SET title = '...' WHERE id = 7` — no need to update thousands of employee rows.
- **Frontend dropdowns**: The `/lookups/job-titles` and `/lookups/departments` endpoints directly power the form dropdowns without deduplication logic.
- **No migration for additions**: Adding a new department is an `INSERT`, not an `ALTER TYPE` (which ENUMs require in Postgres and which is not possible in SQLite).

## Trade-offs

- Slightly more complex queries (require JOIN to resolve names for display).
- Two extra tables to manage. At 15 titles and 10 departments, this is trivial.
- The ORM relationships (`Employee.job_title`, `Employee.department`) with `joinedload` eliminate the N+1 query problem.
