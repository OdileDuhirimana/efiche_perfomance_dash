import { Info, Download, Maximize2 } from "lucide-react";
import { ReactNode } from "react";

interface SectionHeaderProps {
  title: string;
  description?: string;
  showActions?: boolean;
  onInfoClick?: () => void;
  onExportClick?: () => void;
  onMaximizeClick?: () => void;
}

export default function SectionHeader({
  title,
  description,
  showActions = true,
  onInfoClick,
  onExportClick,
  onMaximizeClick,
}: SectionHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-6 md:mb-8 pb-2 sm:pb-3 md:pb-4 border-b border-gray-200">
      <div className="flex items-center gap-2 sm:gap-3 md:gap-4 flex-1">
        <div className="w-0.5 sm:w-1 md:w-1.5 h-5 sm:h-6 md:h-8 bg-gradient-to-b from-blue-600 to-blue-500 rounded-full" />
        <div className="flex-1">
          <h2 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-gray-900 tracking-tight">
            {title}
          </h2>
          {description && (
            <p className="text-xs sm:text-sm text-gray-600 mt-0.5 sm:mt-1 md:mt-1.5">{description}</p>
          )}
        </div>
      </div>
      
      {showActions && (
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onInfoClick}
            className="p-2 rounded-lg hover:bg-blue-50 transition-colors group"
            aria-label="Information"
            title="Information"
          >
            <Info className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
          </button>
          <button
            onClick={onExportClick}
            className="p-2 rounded-lg hover:bg-blue-50 transition-colors group"
            aria-label="Export"
            title="Export"
          >
            <Download className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
          </button>
          <button
            onClick={onMaximizeClick}
            className="p-2 rounded-lg hover:bg-blue-50 transition-colors group"
            aria-label="Maximize"
            title="Maximize"
          >
            <Maximize2 className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
          </button>
        </div>
      )}
    </div>
  );
}

