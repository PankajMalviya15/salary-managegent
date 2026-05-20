/**
 * SWR hooks for lookup data (dropdowns).
 */

"use client";

import useSWR from "swr";
import { get } from "@/lib/api";
import type { JobTitleLookup, DepartmentLookup } from "@/lib/validators";

export function useJobTitles() {
  const { data, error, isLoading } = useSWR<JobTitleLookup[]>(
    "/lookups/job-titles",
    () => get<JobTitleLookup[]>("/lookups/job-titles"),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error };
}

export function useDepartments() {
  const { data, error, isLoading } = useSWR<DepartmentLookup[]>(
    "/lookups/departments",
    () => get<DepartmentLookup[]>("/lookups/departments"),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error };
}

export function useCountries() {
  const { data, error, isLoading } = useSWR<string[]>(
    "/lookups/countries",
    () => get<string[]>("/lookups/countries"),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error };
}
