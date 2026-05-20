/**
 * Insights page — composes all analytics components with country filter.
 */

"use client";

import React, { useState } from "react";
import { Select } from "@/components/ui";
import { useCountries } from "@/hooks/useLookups";
import SalarySummaryCards from "@/components/insights/SalarySummaryCards";
import SalaryByCountryChart from "@/components/insights/SalaryByCountryChart";
import SalaryByJobTitleChart from "@/components/insights/SalaryByJobTitleChart";
import HeadcountChart from "@/components/insights/HeadcountChart";
import OutliersTable from "@/components/insights/OutliersTable";

export default function InsightsPage() {
  const [country, setCountry] = useState<string>("");
  const { data: countries } = useCountries();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Compensation Insights
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Salary analytics and workforce distribution
          </p>
        </div>
        <div className="w-40">
          <Select
            label="Filter Country"
            placeholder="All Countries"
            options={countries.map((c) => ({ value: c, label: c }))}
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
        </div>
      </div>

      {/* Summary Cards */}
      <SalarySummaryCards />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SalaryByCountryChart />
        <HeadcountChart />
      </div>

      {/* Job Title Chart */}
      <SalaryByJobTitleChart country={country || undefined} />

      {/* Outliers */}
      <OutliersTable />
    </div>
  );
}
