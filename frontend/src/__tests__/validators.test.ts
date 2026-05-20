/**
 * Vitest unit tests for lib/validators.ts
 */

import { describe, it, expect } from "vitest";
import { employeeCreateSchema, employeeUpdateSchema } from "../lib/validators";

const VALID_PAYLOAD = {
  full_name: "John Doe",
  email: "john@example.com",
  job_title_id: 1,
  department_id: 1,
  country: "US",
  salary: 100000,
  currency: "USD",
  employment_type: "full-time" as const,
  hire_date: "2024-01-15",
};

describe("employeeCreateSchema", () => {
  it("accepts a valid payload", () => {
    const result = employeeCreateSchema.safeParse(VALID_PAYLOAD);
    expect(result.success).toBe(true);
  });

  it("rejects missing full_name", () => {
    const { full_name, ...rest } = VALID_PAYLOAD;
    const result = employeeCreateSchema.safeParse(rest);
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("full_name");
    }
  });

  it("rejects missing email", () => {
    const { email, ...rest } = VALID_PAYLOAD;
    const result = employeeCreateSchema.safeParse(rest);
    expect(result.success).toBe(false);
  });

  it("rejects invalid email", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      email: "not-an-email",
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("email");
    }
  });

  it("rejects negative salary", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      salary: -5000,
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("salary");
    }
  });

  it("rejects zero salary", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      salary: 0,
    });
    expect(result.success).toBe(false);
  });

  it("rejects lowercase country code", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      country: "us",
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("country");
    }
  });

  it("rejects 3-char country code", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      country: "USA",
    });
    expect(result.success).toBe(false);
  });

  it("rejects future hire date", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      hire_date: "2099-12-31",
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("hire_date");
    }
  });

  it("accepts today as hire date", () => {
    const today = new Date().toISOString().split("T")[0];
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      hire_date: today,
    });
    expect(result.success).toBe(true);
  });

  it("rejects invalid employment type", () => {
    const result = employeeCreateSchema.safeParse({
      ...VALID_PAYLOAD,
      employment_type: "freelance",
    });
    expect(result.success).toBe(false);
  });
});

describe("employeeUpdateSchema", () => {
  it("accepts empty object (no updates)", () => {
    const result = employeeUpdateSchema.safeParse({});
    expect(result.success).toBe(true);
  });

  it("accepts partial update with salary only", () => {
    const result = employeeUpdateSchema.safeParse({ salary: 120000 });
    expect(result.success).toBe(true);
  });

  it("rejects negative salary in update", () => {
    const result = employeeUpdateSchema.safeParse({ salary: -1 });
    expect(result.success).toBe(false);
  });

  it("rejects invalid country in update", () => {
    const result = employeeUpdateSchema.safeParse({ country: "xyz" });
    expect(result.success).toBe(false);
  });
});
