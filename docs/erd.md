# Entity-Relationship Diagram

```mermaid
erDiagram
    JobTitle {
        INTEGER id PK "Auto-increment primary key"
        TEXT title UK "UNIQUE NOT NULL — e.g. 'Software Engineer'"
    }

    Department {
        INTEGER id PK "Auto-increment primary key"
        TEXT name UK "UNIQUE NOT NULL — e.g. 'Engineering'"
    }

    Employee {
        INTEGER id PK "Auto-increment primary key"
        TEXT full_name "NOT NULL, max 200 chars"
        TEXT email UK "UNIQUE NOT NULL"
        INTEGER job_title_id FK "NOT NULL → job_titles.id"
        INTEGER department_id FK "NOT NULL → departments.id"
        TEXT country "NOT NULL, 2-char ISO code (e.g. 'US')"
        REAL salary "NOT NULL, must be > 0"
        TEXT currency "NOT NULL, 3-char (e.g. 'USD'), default 'USD'"
        TEXT employment_type "NOT NULL, default 'full-time'"
        DATE hire_date "NOT NULL, cannot be in future"
        BOOLEAN is_active "NOT NULL, default TRUE (soft delete flag)"
        DATETIME created_at "NOT NULL, server_default now()"
        DATETIME updated_at "NOT NULL, server_default now(), onupdate now()"
    }

    JobTitle ||--o{ Employee : "has many"
    Department ||--o{ Employee : "has many"
```

## Indexes

| Index Name | Table | Columns | Purpose |
|------------|-------|---------|---------|
| `PRIMARY KEY` | `employees` | `id` | Row lookup, keyset pagination cursor |
| `UNIQUE` | `employees` | `email` | Prevent duplicate employee records |
| `ix_emp_country` | `employees` | `country` | Filter/group by country in analytics |
| `ix_emp_jt_country` | `employees` | `job_title_id, country` | Composite: salary-by-job-title-in-country |
| `ix_emp_active` | `employees` | `is_active` | Filter active/inactive employees |
| `UNIQUE` | `job_titles` | `title` | Prevent duplicate titles |
| `UNIQUE` | `departments` | `name` | Prevent duplicate departments |

## Cardinalities

- **JobTitle → Employee**: One-to-many. Each job title can have many employees. Each employee has exactly one job title.
- **Department → Employee**: One-to-many. Each department can have many employees. Each employee belongs to exactly one department.
