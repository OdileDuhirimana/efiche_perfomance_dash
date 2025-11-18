"use client";

interface PerformanceCardProps {
  name: string;
  successRate: number;
  trend?: number; // Optional, not displayed anymore
}

export default function PerformanceCard({
  name,
  successRate,
}: PerformanceCardProps) {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (successRate / 100) * circumference;

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 flex flex-col items-center">
      <div className="text-center mb-4">
        <h3 className="text-base font-semibold text-gray-900 mb-1">{name}</h3>
        <p className="text-xs text-gray-500">Team Member</p>
      </div>
      
      <div className="relative w-32 h-32">
        <svg className="transform -rotate-90 w-32 h-32" viewBox="0 0 128 128">
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
            <p className="text-2xl font-bold text-blue-600">{successRate}%</p>
            <p className="text-xs text-gray-500">Success</p>
          </div>
        </div>
      </div>
    </div>
  );
}

