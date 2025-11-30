import { ReactNode } from "react";
import { LucideIcon, CheckCircle2, CheckCircle } from "lucide-react";

interface KPICardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  target?: {
    text: string;
    met: boolean;
  };
  variant?: "success" | "default";
}

export default function KPICard({
  label,
  value,
  icon: Icon,
  target,
  variant = "default",
}: KPICardProps) {
  const isSuccess = target ? target.met === true : variant === "success";
  const iconColor = isSuccess ? "text-green-500" : "text-gray-400";

  return (
    <div
      className={`rounded-xl p-4 sm:p-5 md:p-6 border-b-4 shadow-md hover:shadow-lg transition-all duration-200 relative overflow-hidden ${
        isSuccess
          ? "bg-gradient-to-br from-green-50 to-white border-b-green-600 border border-gray-200/50"
          : "bg-white border-b-blue-300 border border-gray-200/50"
      }`}
    >
      <div className="flex items-start justify-between mb-2 sm:mb-3 md:mb-4">
        <p className="text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wide">{label}</p>
        <div className={`p-1.5 sm:p-2 rounded-lg ${isSuccess ? "bg-green-100" : "bg-blue-50"}`}>
          <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${iconColor}`} />
        </div>
      </div>
      
      <p
        className={`text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-2 sm:mb-3 md:mb-4 tracking-tight ${
          isSuccess ? "text-green-600" : "text-gray-900"
        }`}
      >
        {value}
      </p>
      
      {target && (
        <div className={`flex items-center gap-2 text-xs font-semibold ${isSuccess ? "text-green-700" : "text-gray-600"}`}>
          <CheckCircle className={`w-4 h-4 ${isSuccess ? "text-green-600" : "text-gray-400"}`} />
          <span>{target.text}</span>
        </div>
      )}
    </div>
  );
}
