/**
 * Main dashboard layout component
 * Displays all dashboard sections in order:
 * 1. Filters (global filter controls)
 * 2. Executive Summary (KPIs)
 * 3. Throughput & Predictability (planned vs done, weekly flow)
 * 4. Quality & Rework (QA metrics, lead time, rework ratio)
 * 5. Ownership & Distribution (task load, execution success)
 * 6. Company-Level Trend (monthly trends)
 */
import Filters from "../components/filters";
import Company_Level_Trend from "./company-level";
import ExecutiveSummary from "./executive-summary";
import Ownership_Distribution from "./ownership-distribution";
import Quality_Rework from "./quality-rework";
import Throughput_Predicatibility from "./throughput-predictability";

export default function DashboardLayout() {
  return (
    <main className="flex-1 md:ml-72 lg:ml-64 p-4 sm:p-6 md:p-7 lg:p-8 pt-20 md:pt-8 bg-gradient-to-br from-gray-50 to-blue-50/30 min-h-screen overflow-x-hidden">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-2 tracking-tight">
          eFiche - Performance Dashboard
        </h1>
        <p className="text-sm sm:text-base text-gray-600">
          Team Performance Dashboard
        </p>
      </div>

      <div className="space-y-4 sm:space-y-6">
      <Filters />
      <ExecutiveSummary />
      <Throughput_Predicatibility />
      <Quality_Rework />
      <Ownership_Distribution />
      <Company_Level_Trend />
      </div>
    </main>
  );
}
