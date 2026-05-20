/**
 * Employee list page — filters, table, pagination, create/edit/delete.
 */

"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { SWRConfig } from "swr";
import { Card, CardHeader, CardContent, Button } from "@/components/ui";
import EmployeeFilterBar from "@/components/employees/EmployeeFilters";
import EmployeeTable from "@/components/employees/EmployeeTable";
import DeleteDialog from "@/components/employees/DeleteDialog";
import { useEmployees, type EmployeeFilters } from "@/hooks/useEmployees";
import type { Employee } from "@/lib/validators";

function EmployeeListContent() {
  const router = useRouter();
  const [filters, setFilters] = useState<EmployeeFilters>({ limit: 20 });
  const { employees, total, nextCursor, isLoading, mutate } = useEmployees(filters);
  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null);

  const handleEdit = (emp: Employee) => {
    router.push(`/employees/${emp.id}`);
  };

  const handleNextPage = () => {
    if (nextCursor) {
      setFilters((prev) => ({ ...prev, cursor: nextCursor }));
    }
  };

  const handlePrevPage = () => {
    setFilters((prev) => ({ ...prev, cursor: null }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Employees
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            {total.toLocaleString()} total employees
          </p>
        </div>
        <Button onClick={() => router.push("/employees/new")}>
          + Add Employee
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent>
          <EmployeeFilterBar filters={filters} onChange={setFilters} />
        </CardContent>
      </Card>

      {/* Table */}
      <EmployeeTable
        employees={employees}
        isLoading={isLoading}
        onEdit={handleEdit}
        onDelete={(emp) => setDeleteTarget(emp)}
      />

      {/* Pagination */}
      {employees.length > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Showing {employees.length} of {total.toLocaleString()}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevPage}
              disabled={!filters.cursor}
            >
              ← First
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextPage}
              disabled={!nextCursor}
            >
              Next →
            </Button>
          </div>
        </div>
      )}

      {/* Delete Dialog */}
      <DeleteDialog
        employee={deleteTarget}
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onDeleted={() => mutate()}
      />
    </div>
  );
}

export default function EmployeesPage() {
  return (
    <SWRConfig value={{ provider: () => new Map() }}>
      <EmployeeListContent />
    </SWRConfig>
  );
}
