/**
 * Employee create/edit form with React Hook Form + Zod validation.
 */

"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input, Select, Button } from "@/components/ui";
import { useJobTitles, useDepartments, useCountries } from "@/hooks/useLookups";
import {
  employeeCreateSchema,
  type EmployeeCreateInput,
  type Employee,
} from "@/lib/validators";

interface Props {
  employee?: Employee; // if provided, edit mode
  onSubmit: (data: EmployeeCreateInput) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export default function EmployeeForm({
  employee,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: Props) {
  const { data: jobTitles } = useJobTitles();
  const { data: departments } = useDepartments();
  const { data: countries } = useCountries();

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<EmployeeCreateInput>({
    resolver: zodResolver(employeeCreateSchema),
    defaultValues: employee
      ? {
          full_name: employee.full_name,
          email: employee.email,
          job_title_id: employee.job_title_id,
          department_id: employee.department_id,
          country: employee.country,
          salary: employee.salary,
          currency: employee.currency,
          employment_type: employee.employment_type as "full-time" | "part-time" | "contract",
          hire_date: employee.hire_date,
        }
      : {
          currency: "USD",
          employment_type: "full-time",
        },
    mode: "onBlur",
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Full Name"
          placeholder="John Doe"
          error={errors.full_name?.message}
          {...register("full_name")}
        />
        <Input
          label="Email"
          type="email"
          placeholder="john@company.com"
          error={errors.email?.message}
          {...register("email")}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Job Title"
          placeholder="Select job title"
          options={jobTitles.map((jt) => ({
            value: jt.id,
            label: jt.title,
          }))}
          error={errors.job_title_id?.message}
          {...register("job_title_id", { valueAsNumber: true })}
        />
        <Select
          label="Department"
          placeholder="Select department"
          options={departments.map((d) => ({
            value: d.id,
            label: d.name,
          }))}
          error={errors.department_id?.message}
          {...register("department_id", { valueAsNumber: true })}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Select
          label="Country"
          placeholder="Select"
          options={countries.map((c) => ({ value: c, label: c }))}
          error={errors.country?.message}
          {...register("country")}
        />
        <div className="relative">
          <Input
            label="Salary"
            type="number"
            step="0.01"
            placeholder="100000"
            error={errors.salary?.message}
            {...register("salary", { valueAsNumber: true })}
          />
        </div>
        <Select
          label="Currency"
          options={[
            { value: "USD", label: "USD" },
            { value: "GBP", label: "GBP" },
            { value: "EUR", label: "EUR" },
            { value: "INR", label: "INR" },
            { value: "CAD", label: "CAD" },
            { value: "AUD", label: "AUD" },
            { value: "JPY", label: "JPY" },
            { value: "BRL", label: "BRL" },
            { value: "SGD", label: "SGD" },
          ]}
          error={errors.currency?.message}
          {...register("currency")}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Employment Type"
          options={[
            { value: "full-time", label: "Full-time" },
            { value: "part-time", label: "Part-time" },
            { value: "contract", label: "Contract" },
          ]}
          error={errors.employment_type?.message}
          {...register("employment_type")}
        />
        <Input
          label="Hire Date"
          type="date"
          error={errors.hire_date?.message}
          {...register("hire_date")}
        />
      </div>

      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-700/50">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting || !isValid}>
          {isSubmitting
            ? "Saving..."
            : employee
            ? "Update Employee"
            : "Create Employee"}
        </Button>
      </div>
    </form>
  );
}
