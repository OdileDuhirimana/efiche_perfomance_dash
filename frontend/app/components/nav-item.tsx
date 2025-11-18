import { NavItemData } from "../types/navigation";
import { ChevronRight } from "lucide-react";

interface NavItemProps {
  item: NavItemData;
  isActive: boolean;
  onClick: () => void;
}

export default function NavItem({ item, isActive, onClick }: NavItemProps) {
  const leftIcon = item.leftIcon || item.icon || <ChevronRight className="w-4 h-4" />;
  const rightIcon = item.rightIcon || <ChevronRight className="w-4 h-4" />;

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
        isActive
          ? "bg-blue-600 text-white shadow-sm"
          : "text-gray-700 hover:bg-gray-50"
      }`}
      aria-current={isActive ? "page" : undefined}
    >
      {/* Left icon */}
      <span
        className={`w-5 h-5 flex items-center justify-center shrink-0 ${
          isActive ? "text-white" : "text-blue-600"
        }`}
      >
        {leftIcon}
      </span>

      {/* Navigation text */}
      <span className="flex-1 text-left">{item.label}</span>

      {/* Right icon */}
      {isActive?
      <span
        className="w-5 h-5 flex items-center justify-center shrink-0 text-white-400">
        {rightIcon}
      </span>: ""}
    </button>
  );
}
