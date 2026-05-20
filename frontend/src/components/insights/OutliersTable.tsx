/**
 * Outliers table — employees >2 SD from peer group mean.
 */

"use client";

import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardContent, Badge, Skeleton } from "@/components/ui";
import { useOutliers } from "@/hooks/useAnalytics";

export default function OutliersTable() {
  const { data, isLoading } = useOutliers();

  if (isLoading) return <Skeleton className="h-64" />;

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-white">Salary Outliers</h3>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500 text-center py-6">
            No outliers detected (all salaries within 2 standard deviations of peer mean)
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-white">
          Salary Outliers
        </h3>
        <p className="text-xs text-slate-400">
          Employees &gt;2 standard deviations from peer group mean
        </p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Title</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400 uppercase">Country</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Salary</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Peer Mean</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400 uppercase">Deviation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/30">
              {data.slice(0, 20).map((emp) => (
                <tr key={emp.id} className="hover:bg-slate-700/20 transition-colors">
                  <td className="px-4 py-3">
                    <Link
                      href={`/employees/${emp.id}`}
                      className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
                    >
                      {emp.full_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{emp.job_title}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant="info">{emp.country}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-white">
                    ${emp.salary.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-400">
                    ${emp.peer_mean.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={emp.deviation > 0 ? "success" : "danger"}>
                      {emp.deviation > 0 ? "+" : ""}
                      {emp.deviation.toFixed(1)}σ
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
