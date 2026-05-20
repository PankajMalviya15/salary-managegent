# ADR-002: Soft Delete Instead of Hard Delete

**Status:** Accepted  
**Date:** 2024-01-15  
**Decision:** Deactivate employees (`is_active = False`) rather than deleting rows.

## Context

When an HR user removes an employee, should the row be deleted from the database or merely flagged as inactive?

## Decision

We chose **soft delete** via an `is_active` boolean column with a dedicated index (`ix_emp_active`).

## Rationale

- **Audit trail**: Payroll systems require historical records. Hard-deleting an employee destroys their compensation history and makes past analytics unreproducible.
- **Reactivation**: A contractor who returns after a gap can be reactivated without re-entering all data.
- **FK safety**: Future tables (reviews, payroll runs) that reference `employees.id` won't suffer cascade deletes.
- **Analytics accuracy**: Historical insight queries (e.g. "what was average salary in Q3?") remain correct because the rows still exist.

## Trade-offs

- Every list query must include `WHERE is_active = TRUE`. The `ix_emp_active` index makes this filter free (B-tree lookup).
- The database grows monotonically. At 10k employees with 5% churn/year, this is negligible for decades.
- A periodic archive job could move very old inactive rows to a separate table if needed.

## Implementation

- `Employee.is_active` defaults to `True`.
- `DELETE /employees/{id}` sets `is_active = False` and returns the updated record.
- `GET /employees` filters by `is_active=True` by default but accepts `?is_active=false` to show deactivated.
