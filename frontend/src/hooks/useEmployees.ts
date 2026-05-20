/**
 * SWR hook for fetching paginated employee list with filters.
 */

"use client";

import useSWR from "swr";
import { get } from "@/lib/api";
import type { PaginatedEmployees } from "@/lib/validators";

export interface EmployeeFilters {
  cursor?: number | null;
  limit?: number;
  country?: string;
  job_title_id?: number;
  department_id?: number;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
  is_active?: boolean;
}

function buildQuery(filters: EmployeeFilters): string {
  const params = new URLSearchParams();
  if (filters.cursor) params.set("cursor", String(filters.cursor));
  if (filters.limit) params.set("limit", String(filters.limit));
  if (filters.country) params.set("country", filters.country);
  if (filters.job_title_id) params.set("job_title_id", String(filters.job_title_id));
  if (filters.department_id) params.set("department_id", String(filters.department_id));
  if (filters.employment_type) params.set("employment_type", filters.employment_type);
  if (filters.salary_min !== undefined) params.set("salary_min", String(filters.salary_min));
  if (filters.salary_max !== undefined) params.set("salary_max", String(filters.salary_max));
  if (filters.is_active !== undefined) params.set("is_active", String(filters.is_active));
  const qs = params.toString();
  return `/employees${qs ? `?${qs}` : ""}`;
}

export function useEmployees(filters: EmployeeFilters = {}) {
  const key = buildQuery(filters);
  const { data, error, isLoading, mutate } = useSWR<PaginatedEmployees>(
    key,
    () => get<PaginatedEmployees>(key),
    { revalidateOnFocus: false }
  );

  return {
    employees: data?.items ?? [],
    total: data?.total ?? 0,
    nextCursor: data?.next_cursor ?? null,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
