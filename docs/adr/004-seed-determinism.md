# ADR-004: Deterministic Seed with Fixed Random Seed

**Status:** Accepted  
**Date:** 2024-01-15  
**Decision:** Use `random.Random(42)` for all random choices in the seed script.

## Context

The seed script generates 10,000 employee records with random names, salaries, countries, and dates. Tests and CI need reproducible data.

## Decision

We chose a **fixed random seed** (`random.Random(42)`) to make the seeder deterministic.

## Rationale

- **Reproducible test fixtures**: Every `make seed` produces the exact same dataset. Tests can assert on specific values without fragility.
- **CI consistency**: The CI pipeline always tests against the same data, eliminating flaky tests caused by random variation.
- **Debuggability**: If a test fails, the developer can reproduce the exact dataset locally by running `make seed`.
- **Benchmarking**: Performance benchmarks are comparable across runs because the data shape is identical.

## Trade-offs

- The generated data is not truly random — it always follows the same pattern. This is a feature, not a bug, for a development tool.
- If you need to test with different data distributions, pass a different seed via environment variable or modify the `Random(42)` constructor.

## Implementation

```python
rng = Random(42)  # deterministic
first = rng.choice(first_names)
salary = round(rng.uniform(salary_min, salary_max), 2)
```
