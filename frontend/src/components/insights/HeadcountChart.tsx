/**
 * Headcount by department donut/pie chart.
 */

"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Card, CardHeader, CardContent, Skeleton } from "@/components/ui";
import { useHeadcount } from "@/hooks/useAnalytics";

const COLORS = [
  "#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6",
  "#fb7185", "#f97316", "#facc15", "#34d399", "#22d3ee",
];

export default function HeadcountChart() {
  const { data, isLoading } = useHeadcount();

  if (isLoading) return <Skeleton className="h-80" />;

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-white">
          Headcount by Department
        </h3>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={120}
              dataKey="count"
              nameKey="group"
              paddingAngle={2}
              stroke="none"
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
              formatter={(value: number, name: string) => [value, name]}
            />
            <Legend
              formatter={(value) => (
                <span className="text-sm text-slate-300">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
