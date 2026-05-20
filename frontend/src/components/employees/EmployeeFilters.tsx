/**
 * Employee filter bar — dropdowns and salary range inputs.
 * Populated from /lookups endpoints.
 */

"use client";

import React from "react";
import { Select, Input, Button } from "@/components/ui";
import { useJobTitles, useDepartments, useCountries } from "@/hooks/useLookups";
import type { EmployeeFilters } from "@/hooks/useEmployees";

interface Props {
  filters: EmployeeFilters;
  onChange: (filters: EmployeeFilters) => void;
}

export default function EmployeeFilterBar({ filters, onChange }: Props) {
  const { data: jobTitles } = useJobTitles();
  const { data: departments } = useDepartments();
  const { data: countries } = useCountries();

  const update = (patch: Partial<EmployeeFilters>) => {
    onChange({ ...filters, ...patch, cursor: null }); // reset cursor on filter change
  };

  const clearAll = () => {
    onChange({ limit: filters.limit });
  };

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="w-36">
        <Select
          label="Country"
          placeholder="All"
          options={countries.map((c) => ({ value: c, label: c }))}
          value={filters.country || ""}
          onChange={(e) =>
            update({ country: e.target.value || undefined })
          }
        />
      </div>

      <div className="w-48">
        <Select
          label="Job Title"
          placeholder="All"
          options={jobTitles.map((jt) => ({
            value: jt.id,
            label: jt.title,
          }))}
          value={filters.job_title_id || ""}
          onChange={(e) =>
            update({
              job_title_id: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        />
      </div>

      <div className="w-44">
        <Select
          label="Department"
          placeholder="All"
          options={departments.map((d) => ({ value: d.id, label: d.name }))}
          value={filters.department_id || ""}
          onChange={(e) =>
            update({
              department_id: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        />
      </div>

      <div className="w-36">
        <Select
          label="Type"
          placeholder="All"
          options={[
            { value: "full-time", label: "Full-time" },
            { value: "part-time", label: "Part-time" },
            { value: "contract", label: "Contract" },
          ]}
          value={filters.employment_type || ""}
          onChange={(e) =>
            update({ employment_type: e.target.value || undefined })
          }
        />
      </div>

      <div className="w-28">
        <Input
          label="Min Salary"
          type="number"
          placeholder="0"
          value={filters.salary_min ?? ""}
          onChange={(e) =>
            update({
              salary_min: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        />
      </div>

      <div className="w-28">
        <Input
          label="Max Salary"
          type="number"
          placeholder="∞"
          value={filters.salary_max ?? ""}
          onChange={(e) =>
            update({
              salary_max: e.target.value ? Number(e.target.value) : undefined,
            })
          }
        />
      </div>

      <Button variant="ghost" size="sm" onClick={clearAll}>
        Clear
      </Button>
    </div>
  );
}
