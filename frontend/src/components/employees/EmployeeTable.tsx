/**
 * Employee data table — sortable columns, row actions, loading/empty states.
 */

"use client";

import React, { useState } from "react";
import { Badge, Button, Skeleton } from "@/components/ui";
import type { Employee } from "@/lib/validators";

interface Props {
  employees: Employee[];
  isLoading: boolean;
  onEdit: (employee: Employee) => void;
  onDelete: (employee: Employee) => void;
}

type SortKey = "full_name" | "job_title" | "country" | "salary" | "hire_date";
type SortDir = "asc" | "desc";

export default function EmployeeTable({
  employees,
  isLoading,
  onEdit,
  onDelete,
}: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("full_name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const sorted = [...employees].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    const cmp =
      typeof aVal === "number" && typeof bVal === "number"
        ? aVal - bVal
        : String(aVal).localeCompare(String(bVal));
    return sortDir === "asc" ? cmp : -cmp;
  });

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return <span className="text-slate-600 ml-1">↕</span>;
    return (
      <span className="text-indigo-400 ml-1">
        {sortDir === "asc" ? "↑" : "↓"}
      </span>
    );
  };

  const columns: { key: SortKey; label: string; className?: string }[] = [
    { key: "full_name", label: "Name" },
    { key: "job_title", label: "Job Title" },
    { key: "country", label: "Country", className: "text-center" },
    { key: "salary", label: "Salary", className: "text-right" },
    { key: "hire_date", label: "Hire Date" },
  ];

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (employees.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-500">
        <svg className="w-16 h-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-lg font-medium">No employees found</p>
        <p className="text-sm mt-1">Try adjusting your filters or add a new employee.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700/50">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700/50 bg-slate-800/80">
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400 cursor-pointer hover:text-white transition-colors ${col.className || ""}`}
                onClick={() => handleSort(col.key)}
              >
                {col.label}
                <SortIcon col={col.key} />
              </th>
            ))}
            <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">
              Status
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700/30">
          {sorted.map((emp) => (
            <tr
              key={emp.id}
              className="group hover:bg-slate-700/20 transition-colors"
            >
              <td className="px-4 py-3">
                <div>
                  <p className="font-medium text-white">{emp.full_name}</p>
                  <p className="text-xs text-slate-500">{emp.email}</p>
                </div>
              </td>
              <td className="px-4 py-3 text-slate-300">{emp.job_title}</td>
              <td className="px-4 py-3 text-center">
                <Badge variant="info">{emp.country}</Badge>
              </td>
              <td className="px-4 py-3 text-right font-mono text-emerald-400">
                {emp.currency}{" "}
                {emp.salary.toLocaleString("en-US", { minimumFractionDigits: 0 })}
              </td>
              <td className="px-4 py-3 text-slate-400">
                {new Date(emp.hire_date).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </td>
              <td className="px-4 py-3 text-center">
                <Badge variant={emp.is_active ? "success" : "danger"}>
                  {emp.is_active ? "Active" : "Inactive"}
                </Badge>
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(emp)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-400 hover:text-red-300"
                    onClick={() => onDelete(emp)}
                  >
                    Delete
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
