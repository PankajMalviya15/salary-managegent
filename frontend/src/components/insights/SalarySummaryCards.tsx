/**
 * Summary metric cards — total employees, avg salary, top country, largest dept.
 */

"use client";

import React from "react";
import { Card, Skeleton } from "@/components/ui";
import { useSalaryByCountry, useHeadcount } from "@/hooks/useAnalytics";
import { useEmployees } from "@/hooks/useEmployees";

export default function SalarySummaryCards() {
  const { total } = useEmployees({ limit: 1 });
  const { data: countryData, isLoading: loadingCountry } = useSalaryByCountry();
  const { data: deptData, isLoading: loadingDept } = useHeadcount();

  const globalAvg =
    countryData.length > 0
      ? countryData.reduce((sum, c) => sum + c.avg_salary * c.employee_count, 0) /
        countryData.reduce((sum, c) => sum + c.employee_count, 0)
      : 0;

  const topCountry = countryData.length > 0 ? countryData[0] : null;
  const topDept = deptData.length > 0 ? deptData[0] : null;

  const cards = [
    {
      label: "Active Employees",
      value: total.toLocaleString(),
      icon: "👥",
      gradient: "from-indigo-500 to-purple-600",
    },
    {
      label: "Avg. Salary",
      value: `$${Math.round(globalAvg).toLocaleString()}`,
      icon: "💰",
      gradient: "from-emerald-500 to-teal-600",
    },
    {
      label: "Top Paying Country",
      value: topCountry ? `${topCountry.country} — $${Math.round(topCountry.avg_salary).toLocaleString()}` : "—",
      icon: "🌍",
      gradient: "from-amber-500 to-orange-600",
    },
    {
      label: "Largest Department",
      value: topDept ? `${topDept.group} (${topDept.count})` : "—",
      icon: "🏢",
      gradient: "from-rose-500 to-pink-600",
    },
  ];

  if (loadingCountry || loadingDept) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.label} className="relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200">
          <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-5 group-hover:opacity-10 transition-opacity`} />
          <div className="relative px-5 py-4">
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                {card.label}
              </p>
              <span className="text-2xl">{card.icon}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-white">{card.value}</p>
          </div>
        </Card>
      ))}
    </div>
  );
}
