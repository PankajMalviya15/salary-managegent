/**
 * Create new employee page.
 */

"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardContent, toast } from "@/components/ui";
import EmployeeForm from "@/components/employees/EmployeeForm";
import { post } from "@/lib/api";
import type { EmployeeCreateInput, Employee } from "@/lib/validators";

export default function NewEmployeePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: EmployeeCreateInput) => {
    setIsSubmitting(true);
    try {
      await post<Employee>("/employees", data);
      toast("Employee created successfully", "success");
      router.push("/employees");
    } catch (err: any) {
      toast(err.message || "Failed to create employee", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          New Employee
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Add a new employee to the system.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <EmployeeForm
            onSubmit={handleSubmit}
            onCancel={() => router.push("/employees")}
            isSubmitting={isSubmitting}
          />
        </CardContent>
      </Card>
    </div>
  );
}
