# ADR-003: Keyset (Cursor) Pagination Over Offset Pagination

**Status:** Accepted  
**Date:** 2024-01-15  
**Decision:** Use keyset pagination (`WHERE id > cursor ORDER BY id LIMIT n`) instead of offset pagination.

## Context

The employee list can contain 10,000+ rows. The frontend needs to paginate through them efficiently.

## Decision

We chose **keyset (cursor) pagination** over traditional offset pagination.

## Rationale

- **O(log n) performance**: Keyset pagination uses the primary key B-tree index regardless of page depth. Offset pagination (`LIMIT n OFFSET k`) must scan and discard the first `k` rows — O(k) work that gets slower as you go deeper.
- **Stable under inserts**: If new employees are added between page fetches, offset pagination can show duplicates or skip rows. Keyset pagination is immune because it uses a stable cursor.
- **Simple API**: `?cursor=<last_id>&limit=20` — the cursor is just the last employee ID seen.

## Trade-offs

- **No arbitrary page jumps**: You cannot navigate directly to "page 47". You must traverse pages sequentially. This is acceptable for an HR tool where users browse sequentially and use filters to narrow results.
- **Cursor must be from a unique, ordered column**: We use the auto-increment `id` primary key, which is guaranteed unique and monotonically increasing.

## Implementation

```python
# Service layer
if cursor:
    query = query.where(Employee.id > cursor)
query = query.order_by(Employee.id).limit(limit + 1)

# Fetch limit+1 rows; if we get more than limit, there's a next page
if len(results) > limit:
    results = results[:limit]
    next_cursor = results[-1].id
```
