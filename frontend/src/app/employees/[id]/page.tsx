/**
 * Edit employee page — loads existing employee and pre-fills form.
 */

"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardContent, Skeleton, toast } from "@/components/ui";
import EmployeeForm from "@/components/employees/EmployeeForm";
import { get, put } from "@/lib/api";
import type { EmployeeCreateInput, Employee } from "@/lib/validators";

export default function EditEmployeePage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    get<Employee>(`/employees/${id}`)
      .then(setEmployee)
      .catch(() => toast("Employee not found", "error"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (data: EmployeeCreateInput) => {
    setIsSubmitting(true);
    try {
      await put<Employee>(`/employees/${id}`, data);
      toast("Employee updated successfully", "success");
      router.push("/employees");
    } catch (err: any) {
      toast(err.message || "Failed to update employee", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="text-center py-16 text-slate-500">
        <p className="text-lg">Employee not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Edit Employee
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Update {employee.full_name}&apos;s information.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <EmployeeForm
            employee={employee}
            onSubmit={handleSubmit}
            onCancel={() => router.push("/employees")}
            isSubmitting={isSubmitting}
          />
        </CardContent>
      </Card>
    </div>
  );
}
