/**
 * Salary by country bar chart using Recharts.
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
import { useSalaryByCountry } from "@/hooks/useAnalytics";

const COLORS = [
  "#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6",
  "#fb7185", "#f97316", "#facc15", "#34d399", "#22d3ee",
];

export default function SalaryByCountryChart() {
  const { data, isLoading } = useSalaryByCountry();

  if (isLoading) {
    return <Skeleton className="h-80" />;
  }

  const chartData = data.map((d) => ({
    ...d,
    avg_salary: Math.round(d.avg_salary),
  }));

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-white">
          Average Salary by Country
        </h3>
        <p className="text-xs text-slate-400">
          Hover for min/max/headcount details
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
            <XAxis
              type="number"
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              stroke="#64748b"
              fontSize={12}
            />
            <YAxis
              type="category"
              dataKey="country"
              width={40}
              stroke="#64748b"
              fontSize={12}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                fontSize: "13px",
              }}
              formatter={(value: number) => [`$${value.toLocaleString()}`, "Avg Salary"]}
              labelFormatter={(label) => `Country: ${label}`}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null;
                const d = payload[0].payload;
                return (
                  <div className="rounded-lg border border-slate-600 bg-slate-800 p-3 shadow-xl text-sm">
                    <p className="font-semibold text-white mb-1">{d.country}</p>
                    <p className="text-emerald-400">Avg: ${d.avg_salary.toLocaleString()}</p>
                    <p className="text-slate-400">Min: ${d.min_salary.toLocaleString()}</p>
                    <p className="text-slate-400">Max: ${d.max_salary.toLocaleString()}</p>
                    <p className="text-indigo-400">Headcount: {d.employee_count}</p>
                  </div>
                );
              }}
            />
            <Bar dataKey="avg_salary" radius={[0, 6, 6, 0]}>
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
