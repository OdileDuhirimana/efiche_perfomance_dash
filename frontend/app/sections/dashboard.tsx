import Filters from "../components/filters";
import Company_Level_Trend from "./company-level";
import ExecutiveSummary from "./executive-summary";
import Ownership_Distribution from "./ownership-distribution";
import Quality_Rework from "./quality-rework";
import Throughput_Predicatibility from "./throughput-predictability";

export default function DashboardLayout() {
  return (
    <main className="flex-1 md:ml-72 lg:ml-64 p-3 sm:p-4 md:p-6 lg:p-8 pt-16 sm:pt-20 md:pt-8 bg-gradient-to-br from-gray-50 to-blue-50/30 min-h-screen overflow-x-hidden">
      <div className="mb-4 sm:mb-6 md:mb-8">
        <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-1 sm:mb-2 tracking-tight">
          eFiche - Performance Dashboard
        </h1>
        <p className="text-xs sm:text-sm md:text-base text-gray-600">
          Team Performance Dashboard
        </p>
      </div>

      <div className="space-y-3 sm:space-y-4 md:space-y-6">
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
