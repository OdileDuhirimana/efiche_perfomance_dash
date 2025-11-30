"use client";

interface PerformanceCardProps {
  name: string;
  successRate: number;
  trend?: number;
}

export default function PerformanceCard({
  name,
  successRate,
}: PerformanceCardProps) {
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (successRate / 100) * circumference;

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 sm:p-5 md:p-6 flex flex-col items-center">
      <div className="text-center mb-3 sm:mb-4">
        <h3 className="text-sm sm:text-base font-semibold text-gray-900 mb-1">{name}</h3>
        <p className="text-xs text-gray-500">Team Member</p>
      </div>
      
      <div className="relative w-24 h-24 sm:w-28 sm:h-28 md:w-32 md:h-32">
        <svg className="transform -rotate-90 w-24 h-24 sm:w-28 sm:h-28 md:w-32 md:h-32" viewBox="0 0 128 128">
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="#2563eb"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg sm:text-xl md:text-2xl font-bold text-blue-600">{successRate}%</p>
            <p className="text-xs text-gray-500">Success</p>
          </div>
        </div>
      </div>
    </div>
  );
}

