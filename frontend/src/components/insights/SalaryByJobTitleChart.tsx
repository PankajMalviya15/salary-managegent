/**
 * Salary by job title grouped bar chart.
 */

"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardHeader, CardContent, Skeleton } from "@/components/ui";
import { useSalaryByJobTitle } from "@/hooks/useAnalytics";

const COLORS = [
  "#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6",
  "#fb7185", "#f97316", "#facc15", "#34d399", "#22d3ee",
  "#38bdf8", "#60a5fa", "#93c5fd", "#7dd3fc", "#67e8f9",
];

interface Props {
  country?: string;
}

export default function SalaryByJobTitleChart({ country }: Props) {
  const { data, isLoading } = useSalaryByJobTitle(country);

  if (isLoading) return <Skeleton className="h-80" />;

  // Aggregate by job title (average across countries)
  const grouped = new Map<string, { total: number; count: number }>();
  data.forEach((d) => {
    const existing = grouped.get(d.job_title) || { total: 0, count: 0 };
    grouped.set(d.job_title, {
      total: existing.total + d.avg_salary * d.employee_count,
      count: existing.count + d.employee_count,
    });
  });

  const chartData = Array.from(grouped.entries())
    .map(([title, { total, count }]) => ({
      job_title: title,
      avg_salary: Math.round(total / count),
      employee_count: count,
    }))
    .sort((a, b) => b.avg_salary - a.avg_salary);

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-white">
          Average Salary by Job Title
        </h3>
        <p className="text-xs text-slate-400">
          {country ? `Filtered: ${country}` : "All countries"}
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData} margin={{ bottom: 60 }}>
            <XAxis
              dataKey="job_title"
              stroke="#64748b"
              fontSize={11}
              angle={-35}
              textAnchor="end"
              height={80}
            />
            <YAxis
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              stroke="#64748b"
              fontSize={12}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null;
                const d = payload[0].payload;
                return (
                  <div className="rounded-lg border border-slate-600 bg-slate-800 p-3 shadow-xl text-sm">
                    <p className="font-semibold text-white mb-1">{d.job_title}</p>
                    <p className="text-emerald-400">Avg: ${d.avg_salary.toLocaleString()}</p>
                    <p className="text-indigo-400">Headcount: {d.employee_count}</p>
                  </div>
                );
              }}
            />
            <Bar dataKey="avg_salary" radius={[6, 6, 0, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
