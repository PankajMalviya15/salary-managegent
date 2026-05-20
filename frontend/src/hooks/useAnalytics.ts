/**
 * SWR hooks for each analytics endpoint.
 */

"use client";

import useSWR from "swr";
import { get } from "@/lib/api";
import type {
  CountrySalarySummary,
  JobTitleSalarySummary,
  HeadcountByGroup,
  SalaryDistribution,
  OutlierEmployee,
} from "@/lib/validators";

export function useSalaryByCountry() {
  const { data, error, isLoading } = useSWR<CountrySalarySummary[]>(
    "/analytics/salary-by-country",
    () => get<CountrySalarySummary[]>("/analytics/salary-by-country"),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error, error };
}

export function useSalaryByJobTitle(country?: string) {
  const path = country
    ? `/analytics/salary-by-job-title?country=${country}`
    : "/analytics/salary-by-job-title";
  const { data, error, isLoading } = useSWR<JobTitleSalarySummary[]>(
    path,
    () => get<JobTitleSalarySummary[]>(path),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error, error };
}

export function useHeadcount() {
  const { data, error, isLoading } = useSWR<HeadcountByGroup[]>(
    "/analytics/headcount",
    () => get<HeadcountByGroup[]>("/analytics/headcount"),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error, error };
}

export function useSalaryDistribution(buckets: number = 10) {
  const path = `/analytics/salary-distribution?buckets=${buckets}`;
  const { data, error, isLoading } = useSWR<SalaryDistribution>(
    path,
    () => get<SalaryDistribution>(path),
    { revalidateOnFocus: false }
  );
  return { data, isLoading, isError: !!error, error };
}

export function useOutliers(threshold: number = 2.0) {
  const path = `/analytics/outliers?threshold=${threshold}`;
  const { data, error, isLoading } = useSWR<OutlierEmployee[]>(
    path,
    () => get<OutlierEmployee[]>(path),
    { revalidateOnFocus: false }
  );
  return { data: data ?? [], isLoading, isError: !!error, error };
}
