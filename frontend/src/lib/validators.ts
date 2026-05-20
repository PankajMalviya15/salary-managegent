/**
 * Zod schemas mirroring backend Pydantic models.
 * Single source of truth for frontend validation.
 */

import { z } from "zod";

// ── Employee Create ───────────────────────────────────────────────

export const employeeCreateSchema = z.object({
  full_name: z.string().min(1, "Name is required").max(200),
  email: z.string().email("Invalid email address"),
  job_title_id: z.number().int().positive("Job title is required"),
  department_id: z.number().int().positive("Department is required"),
  country: z
    .string()
    .length(2, "Country must be a 2-character code")
    .regex(/^[A-Z]{2}$/, "Country must be uppercase (e.g. US)"),
  salary: z.number().positive("Salary must be greater than 0"),
  currency: z.string().length(3).default("USD"),
  employment_type: z.enum(["full-time", "part-time", "contract"]).default("full-time"),
  hire_date: z.string().refine(
    (val) => {
      const d = new Date(val);
      return !isNaN(d.getTime()) && d <= new Date();
    },
    { message: "Hire date cannot be in the future" }
  ),
});

export type EmployeeCreateInput = z.infer<typeof employeeCreateSchema>;

// ── Employee Update (all optional) ────────────────────────────────

export const employeeUpdateSchema = z.object({
  full_name: z.string().min(1).max(200).optional(),
  email: z.string().email().optional(),
  job_title_id: z.number().int().positive().optional(),
  department_id: z.number().int().positive().optional(),
  country: z
    .string()
    .length(2)
    .regex(/^[A-Z]{2}$/)
    .optional(),
  salary: z.number().positive().optional(),
  currency: z.string().length(3).optional(),
  employment_type: z.enum(["full-time", "part-time", "contract"]).optional(),
  hire_date: z
    .string()
    .refine((val) => {
      const d = new Date(val);
      return !isNaN(d.getTime()) && d <= new Date();
    })
    .optional(),
});

export type EmployeeUpdateInput = z.infer<typeof employeeUpdateSchema>;

// ── Response types (read-only, not validated on submit) ───────────

export interface Employee {
  id: number;
  full_name: string;
  email: string;
  job_title_id: number;
  department_id: number;
  job_title: string;
  department: string;
  country: string;
  salary: number;
  currency: string;
  employment_type: string;
  hire_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedEmployees {
  items: Employee[];
  total: number;
  next_cursor: number | null;
}

export interface CountrySalarySummary {
  country: string;
  min_salary: number;
  max_salary: number;
  avg_salary: number;
  employee_count: number;
}

export interface JobTitleSalarySummary {
  job_title: string;
  country: string;
  avg_salary: number;
  employee_count: number;
}

export interface HeadcountByGroup {
  group: string;
  count: number;
}

export interface SalaryBucket {
  bucket_min: number;
  bucket_max: number;
  count: number;
}

export interface SalaryDistribution {
  buckets: SalaryBucket[];
  total: number;
}

export interface OutlierEmployee {
  id: number;
  full_name: string;
  email: string;
  job_title: string;
  country: string;
  salary: number;
  peer_mean: number;
  peer_std: number;
  deviation: number;
}

export interface JobTitleLookup {
  id: number;
  title: string;
}

export interface DepartmentLookup {
  id: number;
  name: string;
}
