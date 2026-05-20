# Data Flow Diagram

## Request/Response Flow

The following diagram shows the complete data flow for a typical API request, from browser to database and back.

```mermaid
sequenceDiagram
    participant B as Browser (React)
    participant N as Next.js (Proxy)
    participant F as FastAPI
    participant P as Pydantic
    participant S as SQLAlchemy
    participant D as SQLite

    Note over B,N: Same-origin request via Next.js rewrites

    B->>N: GET /api/v1/employees?cursor=50&limit=20
    N->>F: Proxy → GET /api/v1/employees?cursor=50&limit=20

    Note over F: Request logging middleware starts timer

    F->>P: Validate query params (cursor: int, limit: int)
    P-->>F: Validated params

    F->>S: employee_service.list_employees(db, cursor=50, limit=20)
    S->>D: SELECT * FROM employees WHERE id > 50 AND is_active = 1 ORDER BY id LIMIT 21
    D-->>S: Row objects
    S-->>F: List[Employee] ORM objects

    F->>P: Serialize via EmployeeRead response_model
    P-->>F: JSON-serializable dict

    Note over F: Request logging middleware logs: GET /employees → 200 (12ms)

    F-->>N: HTTP 200 JSON {items, total, next_cursor}
    N-->>B: Proxied response

    Note over B: SWR caches response, renders EmployeeTable
```

## Write Flow (Create Employee)

```mermaid
sequenceDiagram
    participant B as Browser (React)
    participant N as Next.js (Proxy)
    participant F as FastAPI
    participant P as Pydantic
    participant S as SQLAlchemy
    participant D as SQLite

    B->>N: POST /api/v1/employees {full_name, email, salary, ...}
    N->>F: Proxy → POST

    F->>P: Validate body via EmployeeCreate schema
    Note over P: Checks: salary > 0, country 2-char uppercase,<br/>hire_date not future, email format

    alt Validation fails
        P-->>F: ValidationError
        F-->>N: HTTP 422 {detail: [{loc, msg, type}]}
        N-->>B: 422 error
    else Validation passes
        P-->>F: EmployeeCreate object
        F->>S: employee_service.create_employee(db, data)
        S->>D: INSERT INTO employees (...) VALUES (...)
        alt Duplicate email
            D-->>S: IntegrityError
            S-->>F: HTTPException(409)
            F-->>N: HTTP 409 "An employee with this email already exists"
        else Success
            D-->>S: OK
            S-->>F: Employee ORM object (with id, created_at)
            F->>P: Serialize via EmployeeRead response_model
            F-->>N: HTTP 201 {id, full_name, ...}
        end
        N-->>B: Response
    end

    Note over B: SWR mutate() revalidates employee list
```

## Validation Boundaries

| Layer | What is validated |
|-------|-------------------|
| **Browser (Zod)** | Client-side: salary > 0, country format, email format, hire_date not future. Provides instant feedback. |
| **FastAPI (Pydantic)** | Server-side: identical rules as Zod + EmailStr validation. Authoritative — never trust the client. |
| **SQLAlchemy** | Schema-level: NOT NULL, UNIQUE email, FK constraints. Last line of defense. |
| **SQLite** | Storage-level: data types, index enforcement. |
